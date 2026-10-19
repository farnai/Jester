// Real Chrome, Supabase Auth, FastAPI and database. Offline mode injects failures;
// no mocked business responses or fabricated sessions. Only manifest QA users.
const { chromium } = require('playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const accounts = JSON.parse(fs.readFileSync('scratch/wave4-accounts.json','utf8'));
const out = '.jester/reports/verification/wave4-messaging';
fs.mkdirSync(out,{recursive:true});
const base='http://127.0.0.1:3001';
const evidence={checks:[],measurements:[],realtimeEvents:[],pageErrors:[]};
const pass=name=>{evidence.checks.push(name);console.log('PASS:',name);};
async function api(page,route,method='GET',body) {
  return page.evaluate(async ({route,method,body})=>{
    const key=Object.keys(localStorage).find(k=>k.endsWith('-auth-token'));
    const session=JSON.parse(localStorage.getItem(key));
    const r=await fetch('http://127.0.0.1:8000'+route,{method,headers:{Authorization:'Bearer '+session.access_token,'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
    return {status:r.status,data:await r.json()};
  },{route,method,body});
}
async function until(fn,description,timeout=20000) {
  const end=Date.now()+timeout;
  while(Date.now()<end){if(await fn())return;await new Promise(r=>setTimeout(r,200));}
  throw new Error('Timed out: '+description);
}
async function login(page,account) {
  await page.goto(base+'/auth/login');await page.locator('#login-email').fill(account.email);
  await page.locator('#login-password').fill(account.password);await page.locator('.login-submit').click();
  await page.waitForURL(u=>!u.pathname.startsWith('/auth'),{timeout:30000});
}
async function send(page,body) {
  await page.getByRole('textbox',{name:'შეტყობინება',exact:true}).fill(body);
  await page.getByRole('button',{name:'გაგზავნა',exact:true}).click();
  await page.locator('.chat-message p').filter({hasText:body}).waitFor();
}
async function shot(page,name) {
  await page.waitForTimeout(300);
  await page.screenshot({path:`${out}/${name}.png`,fullPage:true});
}
async function layout(page,width,height,name) {
  await page.setViewportSize({width,height});
  await page.waitForTimeout(300);
  const m=await page.evaluate(()=>{
    const form=document.querySelector('.chat-composer').getBoundingClientRect();
    const nav=document.querySelector('.home-mobile-navigation');
    const r=nav?.getBoundingClientRect();
    return {width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,
      composerTop:form.top,composerBottom:form.bottom,navTop:r?.height?r.top:innerHeight,
      sendHeight:document.querySelector('.chat-composer button').getBoundingClientRect().height};
  });
  evidence.measurements.push(m);
  assert(m.scrollWidth<=width,'horizontal overflow');assert(m.composerTop>=0,'composer above viewport');
  assert(m.composerBottom<=m.navTop+1,`composer overlaps navigation: ${JSON.stringify(m)}`);assert(m.sendHeight>=44);
  await shot(page,name);
}
(async()=>{
  const browser=await chromium.launch({headless:true,channel:'chrome'});
  try {
    const ca=await browser.newContext({viewport:{width:1440,height:900}});
    const cb=await browser.newContext({viewport:{width:1280,height:800}});
    const a=await ca.newPage(),b=await cb.newPage();
    for(const [label,page] of [['A',a],['B',b]]) {
      page.on('pageerror',e=>evidence.pageErrors.push({user:label,message:e.message}));
      page.on('websocket',ws=>ws.on('framereceived',({payload})=>{
        try {const raw=JSON.parse(payload.toString());const x=Array.isArray(raw)?{event:raw[3],payload:raw[4]}:raw;if(x.event==='postgres_changes')evidence.realtimeEvents.push({user:label,table:x.payload?.data?.table,type:x.payload?.data?.type});}catch{}
      }));
    }
    await login(a,accounts[0]);await login(b,accounts[1]);
    await b.goto(base+'/messages');
    const initialInbox=(await api(b,'/v1/conversations')).data;
    if(!initialInbox.length)await b.getByRole('heading',{name:'პირველი საუბარი წინ არის',exact:true}).waitFor();
    await cb.setOffline(true);
    await until(async()=>await b.getByText('საუბრები ვერ ჩაიტვირთა.',{exact:true}).isVisible(),'inbox offline error');
    await b.getByRole('button',{name:'ხელახლა ცდა',exact:true}).click();await cb.setOffline(false);
    await until(async()=>!await b.getByText('საუბრები ვერ ჩაიტვირთა.',{exact:true}).isVisible(),'inbox retry');
    pass('Real inbox empty state and offline error/retry recover without invented rows');
    // Re-run safety: only this exact manifest pair is eligible for reset.
    const prior=(await api(a,'/v1/connections')).data.find(c=>[c.user_a_id,c.user_b_id].includes(accounts[1].id));
    if(prior) {
      const actor=prior.blocked_by===accounts[1].id?b:a;
      assert.equal((await api(actor,`/v1/connections/${prior.id}/transition`,'POST',{action:prior.status==='blocked'?'unblock':'remove'})).status,200);
    }
    await a.goto(base+'/discover?q=QA+W4');await a.locator('.discover-swipe-card').waitFor();
    assert.equal(await a.locator('.discover-swipe-card').getAttribute('data-person-id'),accounts[1].id);
    await a.getByRole('button',{name:'დაკავშირება',exact:true}).click();
    await a.getByRole('button',{name:'მოთხოვნის გაგზავნა',exact:true}).click();
    await a.locator('.connection-actions[data-state="pending_out"]').waitFor();
    const connection=(await api(a,'/v1/connections')).data.find(c=>[c.user_a_id,c.user_b_id].includes(accounts[1].id));
    const transition=(actor,action)=>api(actor,`/v1/connections/${connection.id}/transition`,'POST',{action});
    await b.goto(base+'/connections?tab=incoming');await b.getByRole('button',{name:'მოთხოვნის მიღება',exact:true}).click();
    await a.locator('.connection-actions[data-state="accepted"]').waitFor();
    await shot(a,'discover-connected-desktop');
    await b.goto(base+'/connections');await b.locator('.connection-row').waitFor();await shot(b,'connections-desktop');
    pass('Two genuine Auth accounts: Discover request → incoming acceptance → live accepted state across surfaces');
    await a.getByRole('button',{name:'საუბარი',exact:true}).click();await a.waitForURL(/\/chat\//);
    const conv=new URL(a.url()).pathname.split('/').pop(),route=`/v1/conversations/${conv}`;
    await a.locator('.chat-composer').waitFor();
    // Existing messages from a rerun must first be acknowledged, without deletion.
    const previous=(await api(b,route+'/messages/page')).data.items;
    if(previous.length)await api(b,route+'/read','PATCH',{last_read_message_id:previous[previous.length-1].id});
    const stamp=Date.now(),hello=`გამარჯობა! ხელოვნებაზე საუბარი ხომ არ დავიწყოთ? ${stamp}`;
    await send(a,hello);await b.goto(base+'/messages');
    await b.locator('.inbox-row').waitFor();
    assert.equal(await b.locator('.inbox-row').getAttribute('data-conversation-id'),conv);
    await until(async()=>await b.locator('.inbox-unread').textContent()==='1','actual unread badge');
    assert((await b.locator('.inbox-copy').innerText()).includes('ანა'));
    assert((await b.locator('.inbox-copy').innerText()).includes(hello));
    await b.waitForFunction(()=>document.querySelector('.inbox-row img')?.naturalWidth>0);
    assert((await api(b,'/v1/conversations')).data[0].last_activity_at);
    await shot(b,'inbox-unread-desktop');
    for(const width of [390,320]){await b.setViewportSize({width,height:844});await shot(b,`inbox-${width}`);assert(await b.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));}
    pass('Real inbox uses participant private photograph, name, persisted preview/activity and nonzero unread');
    await b.locator('.inbox-row').click();await b.locator('.chat-message p').filter({hasText:hello}).waitFor();
    await until(async()=>(await api(b,'/v1/conversations')).data[0].unread_count===0,'read boundary persisted');
    const eventsBefore=evidence.realtimeEvents.length;
    const reply=`კი, გამოფენებით დავიწყოთ. ${stamp}`;
    await send(b,reply);await a.locator('.chat-message p').filter({hasText:reply}).waitFor();
    await until(()=>evidence.realtimeEvents.slice(eventsBefore).some(e=>e.user==='A'&&e.table==='messages'),'actual Supabase message event');
    assert.equal(await a.locator('.chat-message p').filter({hasText:reply}).count(),1);
    await a.reload();await a.locator('.chat-message p').filter({hasText:reply}).waitFor();
    pass('Bidirectional human messages, actual Realtime postgres event, no duplicates, reload and read-state persistence');
    await a.locator('.chat-starters summary').click();
    await a.locator('.chat-starters button').first().waitFor();
    const starter=await a.locator('.chat-starters button').first().textContent();
    assert(!starter.includes('ხელახლა ცდა'),'actual Why starter available');
    await a.locator('.chat-starters button').first().click();
    assert.equal(await a.getByRole('textbox',{name:'შეტყობინება',exact:true}).inputValue(),starter);
    await a.getByRole('textbox',{name:'შეტყობინება',exact:true}).fill('');
    pass('Existing authorized JESTER Why insight supplies an editable starter, without sending automatically');
    const retry=`ქსელის დაბრუნების შემდეგაც ეს ტექსტი შენარჩუნდება. ${stamp}`;
    await ca.setOffline(true);
    await a.getByRole('textbox',{name:'შეტყობინება',exact:true}).fill(retry);
    await a.getByRole('button',{name:'გაგზავნა',exact:true}).click();
    await a.locator('.chat-send-error').waitFor();
    await a.waitForTimeout(5500);
    assert.equal(await a.getByRole('textbox',{name:'შეტყობინება',exact:true}).inputValue(),retry);
    await ca.setOffline(false);await a.getByRole('button',{name:'ხელახლა გაგზავნა',exact:true}).click();
    await a.locator('.chat-message p').filter({hasText:retry}).waitFor();
    assert.equal((await api(a,route+'/messages/page')).data.items.filter(m=>m.body===retry).length,1);
    pass('Real network failure retains draft; explicit retry persists exactly one message');
    await cb.setOffline(true);
    const missed=`კავშირის აღდგენისას ეს შეტყობინებაც გამოჩნდება. ${stamp}`;
    await send(a,missed);await cb.setOffline(false);
    await b.locator('.chat-message p').filter({hasText:missed}).waitFor();
    pass('Offline recipient resynchronizes missed messages when connectivity returns');
    for(let i=0;i<33;i++)assert.equal((await api(b,route+'/messages','POST',{body:`საუბრის ისტორია ${i+1} · ${stamp}`,client_nonce:crypto.randomUUID()})).status,201);
    await a.reload();await a.locator('.chat-older').waitFor();
    await until(async()=>await a.locator('.chat-message').count()===30,'bounded first page');
    const older=await api(a,route+'/messages/page');assert.equal(older.data.items.length,30);assert(older.data.next_cursor);
    await a.locator('.chat-older').click();
    await until(async()=>await a.locator('.chat-message').count()>30,'older page');
    const ids=await a.locator('.chat-message').evaluateAll(els=>els.map(e=>e.dataset.messageId));assert.equal(new Set(ids).size,ids.length);
    await a.getByRole('button',{name:'ბოლო შეტყობინებებზე ↓',exact:true}).click();
    pass('History first page is 30; cursor loads older real messages without duplicates or replacing current history');
    await send(a,'შაბათს ფოტოგამოფენაზე წასვლას ვაპირებ. შენ რომელი ჟანრი გაინტერესებს?');
    await send(b,'ქუჩის ფოტოგრაფია განსაკუთრებით მიყვარს. სიამოვნებით განვაგრძობ ამ საუბარს!');
    await a.locator('.chat-message p').filter({hasText:'ქუჩის ფოტოგრაფია განსაკუთრებით'}).last().waitFor();
    for(const [w,h] of [[1440,900],[1280,800],[390,844],[320,700]])await layout(a,w,h,`chat-${w}`);
    await a.getByRole('textbox',{name:'შეტყობინება',exact:true}).focus();
    await layout(a,320,440,'chat-320-reduced-viewport');
    pass('Desktop 1440/1280, mobile 390/320 and reduced-height focused composer: no overflow/overlap; send target ≥44px');
    await a.setViewportSize({width:390,height:844});await a.goto(base+'/connections');await a.locator('.connection-row').waitFor();await shot(a,'connections-390');
    a.once('dialog',d=>d.accept());await a.getByRole('button',{name:'კავშირის გაუქმება',exact:true}).click();
    await b.getByRole('heading',{name:'საუბარი მიუწვდომელია',exact:true}).waitFor();
    assert.equal((await api(b,route+'/messages','POST',{body:'must fail'})).status,404);
    assert.equal((await api(b,'/v1/conversations')).data.length,0);
    pass('Removing connection revokes existing chat and inbox without reloading the recipient');
    // Decline and outgoing cancellation use the same canonical pair, then reconnect.
    assert.equal((await api(a,'/v1/connections','POST',{target_user_id:accounts[1].id})).status,201);
    await b.goto(base+'/connections?tab=incoming');await b.getByRole('button',{name:'უარყოფა',exact:true}).click();
    await until(async()=>(await api(a,'/v1/connections')).data[0].status==='declined','declined persisted');
    assert.equal((await api(a,'/v1/connections','POST',{target_user_id:accounts[1].id})).status,201);
    await a.goto(base+'/connections?tab=outgoing');a.once('dialog',d=>d.accept());await a.getByRole('button',{name:'მოთხოვნის გაუქმება',exact:true}).click();
    await until(async()=>(await api(a,'/v1/connections')).data[0].status==='removed','cancel persisted');
    assert.equal((await api(a,'/v1/connections','POST',{target_user_id:accounts[1].id})).status,201);
    await b.goto(base+'/connections?tab=incoming');await b.getByRole('button',{name:'მოთხოვნის მიღება',exact:true}).click();
    await until(async()=>(await api(a,'/v1/connections')).data[0].status==='accepted','reaccept');
    assert.equal((await api(a,'/v1/conversations','POST',{target_user_id:accounts[1].id})).data.id,conv);
    pass('Decline, outgoing cancellation and reacceptance persist on the canonical pair; conversation is reused');
    await b.goto(base+'/chat/'+conv);await b.locator('.chat-composer').waitFor();
    await a.goto(base+'/connections');a.once('dialog',d=>d.accept());await a.getByRole('button',{name:'დაბლოკვა',exact:true}).click();
    await b.getByRole('heading',{name:'საუბარი მიუწვდომელია',exact:true}).waitFor();
    for(const action of ['remove','block','unblock'])assert.equal((await transition(b,action)).status,404);
    assert.equal((await transition(a,'remove')).status,400);
    for(const actor of [a,b]){
      assert.equal((await api(actor,route)).status,404);assert.equal((await api(actor,route+'/messages/page')).status,404);
      assert.equal((await api(actor,route+'/messages','POST',{body:'blocked send'})).status,404);
      assert.equal((await api(actor,route+'/read','PATCH',{last_read_message_id:ids[0]})).status,404);
      assert.equal((await api(actor,'/v1/conversations')).data.length,0);
    }
    await a.goto(base+'/connections?tab=blocked');await a.getByRole('button',{name:'ბლოკის მოხსნა',exact:true}).waitFor();await shot(a,'blocked-390');
    await shot(b,'chat-blocked-320');
    assert.equal((await transition(a,'unblock')).data.status,'removed');
    assert.equal((await api(b,route+'/messages','POST',{body:'still disconnected'})).status,404);
    pass('Block removes chat access for both; blocked actor cannot remove/steal/unblock; authorized unblock leaves disconnected');
    assert.deepEqual(evidence.pageErrors,[]);
    pass('Zero uncaught browser application errors');
  } catch(error) { evidence.failure=error.message;throw error; }
  finally {fs.writeFileSync(`${out}/evidence.json`,JSON.stringify(evidence,null,2));await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
