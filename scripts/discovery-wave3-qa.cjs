// Real Chrome + local Supabase/FastAPI. No route mocks or fabricated sessions.
const { chromium } = require('playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const accounts = JSON.parse(fs.readFileSync('scratch/wave3-accounts.json', 'utf8'));
const out = '.jester/reports/verification/wave3-discovery';
fs.mkdirSync(out, { recursive: true });
const base = 'http://127.0.0.1:3001';
const evidence = { checks: [], measurements: [], media: [], pageErrors: [] };
function pass(name) { evidence.checks.push(name); console.log('PASS:', name); }
async function api(page, route, method = 'GET', body) {
  return page.evaluate(async ({ route, method, body }) => {
    const key = Object.keys(localStorage).find(k => k.endsWith('-auth-token'));
    const session = JSON.parse(localStorage.getItem(key));
    const r = await fetch('http://127.0.0.1:8000' + route, { method,
      headers: { Authorization: 'Bearer ' + session.access_token, 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body) });
    return { status: r.status, data: await r.json() };
  }, { route, method, body });
}
async function login(page, account) {
  await page.goto(base + '/auth/login');
  await page.locator('#login-email').fill(account.email);
  await page.locator('#login-password').fill(account.password);
  await page.locator('.login-submit').click();
  await page.waitForURL(u => !u.pathname.startsWith('/auth'), { timeout: 30000 });
}
async function ready(page) {
  await page.locator('.discover-swipe-card').waitFor();
  await page.locator('.discover-photo-layer:not(.is-preload) img').waitFor();
  await page.waitForFunction(() => document.querySelector('.discover-photo-layer:not(.is-preload) img')?.naturalWidth > 0);
}
async function swipe(page, dx, dy = 0) {
  const box = await page.locator('.discover-photo').boundingBox();
  const x=box.x+box.width/2, y=box.y+box.height/2;
  await page.mouse.move(x,y); await page.mouse.down();
  await page.mouse.move(x+dx,y+dy,{steps:12}); await page.mouse.up();
}
(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    page.on('pageerror', e => evidence.pageErrors.push(e.message));
    await login(page, accounts[0]);
    const query = new URLSearchParams({ q:'QA W3' });
    // Repeatable against only these fixture pairs.
    for (const connection of (await api(page,'/v1/connections')).data) {
      if (accounts.some(a=>a.id!==accounts[0].id && [connection.user_a_id,connection.user_b_id].includes(a.id))) {
        const action=connection.status==='blocked'?'unblock':'remove';
        const r=await api(page,`/v1/connections/${connection.id}/transition`,'POST',{action});
        assert.equal(r.status,200);
      }
    }
    const response = await api(page, '/v1/discovery/people?'+query);
    assert.equal(response.status,200); assert.equal(response.data.items.length,3);
    const people=response.data.items;
    assert(!people.some(p => p.id === accounts[0].id));
    const target=people[0];
    const targetAccount=accounts.find(a=>a.id===target.id);
    let media=[];
    page.on('request', r => { if (/\/photos\/[^/]+\/content/.test(r.url()) && !r.url().includes(accounts[0].id)) media.push(r.url()); });
    await page.goto(base+'/discover?'+query); await ready(page);
    await page.waitForTimeout(500);
    const uniqueMedia=[...new Set(media)];
    assert.equal(uniqueMedia.length,2);
    assert(uniqueMedia.every(url=>url.endsWith('?size=card')));
    assert(uniqueMedia.every(url=>[people[0].id,people[1].id].some(id=>url.includes(id))));
    evidence.media=uniqueMedia.map(url=>url.replace('http://127.0.0.1:8000',''));
    pass('Initial deck loads only current and next candidate card media; excludes self; three genuine fixture people');
    await page.getByRole('button',{name:'შემდეგი ფოტო',exact:true}).click();
    await page.getByLabel('ფოტო 2 / 2',{exact:true}).waitFor();
    const photo=await page.locator('.discover-photo').boundingBox();
    await page.mouse.click(photo.x+30,photo.y+photo.height/2);
    await page.getByLabel('ფოტო 1 / 2',{exact:true}).waitFor();
    pass('Photo button and tap regions switch real gallery images');
    await swipe(page,100);
    await page.locator('dialog[open]').waitFor();
    assert.equal(await page.getByRole('button',{name:'ჯერ არა',exact:true}).evaluate(el=>el===document.activeElement),true);
    await page.keyboard.press('Escape');
    assert.equal((await api(page,'/v1/connections')).data.filter(c=>c.status==='pending').length,0);
    pass('Right swipe opens focused confirmation; Escape cancels without request');
    await swipe(page,0,-80);
    assert.equal(await page.locator('.discover-swipe-card').getAttribute('data-person-id'),target.id);
    await swipe(page,-100);
    await page.waitForFunction(id=>document.querySelector('.discover-swipe-card')?.dataset.personId!==id,target.id);
    const secondId=await page.locator('.discover-swipe-card').getAttribute('data-person-id');
    await page.locator('.discover-card-actions > a').click();
    await page.locator('.social-story h1').waitFor();
    assert.equal(await page.locator('.person-details').getAttribute('open'),null);
    assert.equal(await page.getByRole('link',{name:/Why/}).count(),0);
    await page.getByRole('link',{name:'← აღმოჩენაზე დაბრუნება',exact:true}).click();
    await ready(page);
    assert.equal(await page.locator('.discover-swipe-card').getAttribute('data-person-id'),secondId);
    assert(new URL(page.url()).searchParams.get('q')==='QA W3');
    pass('Vertical movement does not advance; left swipe advances; profile return preserves person/filter; strangers see no Why');
    await page.locator('.discover-card-actions > a').click();
    await page.locator('.social-story h1').waitFor(); await page.goBack(); await ready(page);
    assert.equal(await page.locator('.discover-swipe-card').getAttribute('data-person-id'),secondId);
    await page.locator('.discover-photo').focus(); await page.keyboard.press('ArrowLeft');
    await page.waitForFunction(id=>document.querySelector('.discover-swipe-card')?.dataset.personId!==id,secondId);
    pass('Browser Back and keyboard Next preserve usable deck navigation');
    await page.goto(base+'/discover?'+query); await ready(page);
    await page.locator('.discover-photo').focus(); await page.keyboard.press('ArrowRight');
    await page.locator('dialog[open]').waitFor();
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:`${out}/connection-confirmation-390x844.png`});
    await page.setViewportSize({width:1440,height:900});
    await page.getByRole('button',{name:'მოთხოვნის გაგზავნა',exact:true}).click();
    await page.locator('.connection-actions[data-state=pending_out]').waitFor();
    const targetContext=await browser.newContext({viewport:{width:390,height:844}});
    const other=await targetContext.newPage(); await login(other,targetAccount);
    await other.goto(base+'/people/'+accounts[0].id);
    await other.locator('.connection-actions[data-state=pending_in]').waitFor();
    await other.getByRole('button',{name:'მოთხოვნის მიღება',exact:true}).click();
    await other.locator('.connection-actions[data-state=accepted]').waitFor();
    await page.reload(); await ready(page);
    await page.locator('.connection-actions[data-state=accepted]').waitFor();
    pass('Confirmed request persists; recipient receives pending_in and accepts; sender sees accepted');
    const sizes=[[1440,900],[1280,800],[390,844],[320,700]];
    async function capture(surface) {
      for (const [width,height] of sizes) {
        await page.setViewportSize({width,height}); await page.evaluate(()=>window.scrollTo(0,0));
        await page.evaluate(()=>document.fonts.ready); await page.waitForTimeout(300);
        const measure=await page.evaluate(surface=>{
          const el=document.querySelector(surface==='discover'?'.discover-card-actions':'.person-connection-bar');
          const rect=el.getBoundingClientRect();
          const nav=document.querySelector('.home-mobile-navigation');
          return {width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,actionsTop:Math.round(rect.top),actionsBottom:Math.round(rect.bottom),navTop:nav?Math.round(nav.getBoundingClientRect().top):null};
        },surface);
        evidence.measurements.push({surface,...measure});
        assert.equal(measure.scrollWidth,width,'horizontal overflow');
        if (width <= 700) assert(measure.actionsBottom <= measure.navTop, 'actions must stay above bottom navigation');
        assert(measure.actionsTop >= 0 && measure.actionsBottom <= height, 'primary actions must be visible without scrolling');
        await page.screenshot({path:`${out}/${surface}-${width}x${height}.png`});
        if(width===1440 || width===320) await page.screenshot({path:`${out}/${surface}-${width}-full.png`,fullPage:true});
      }
    }
    await capture('discover');
    await page.locator('.discover-card-actions > a').click();
    await page.locator('.social-portrait img').waitFor();
    await page.getByRole('link',{name:/Why/}).waitFor();
    await page.waitForFunction(()=>!document.querySelector('.person-preview [role=status]'));
    await capture('person');
    await page.locator('.person-details summary').click();
    await page.locator('.person-details .social-tags span').first().waitFor();
    await page.getByRole('button',{name:'საუბარი',exact:true}).click();
    await page.waitForURL(/\/chat\//);
    pass('Accepted profile exposes Why and real direct conversation; astrology expands on demand; four responsive screenshots captured');
    await page.setViewportSize({width:1440,height:900});
    await page.goto(base+'/discover'); await page.locator('.discover-swipe-card').waitFor();
    await page.locator('#people-search').fill('QA W3');
    await page.getByRole('button',{name:'ძებნა',exact:true}).click(); await ready(page);
    const cityResponse=page.waitForResponse(r=>r.url().includes('/v1/discovery/people?')&&r.url().includes('city_id='));
    const geoResponse=page.waitForResponse(r=>r.url().includes('/v1/geo/cities')&&r.url().includes('Tbilisi'));
    await page.getByLabel('ქალაქი',{exact:true}).fill('Tbilisi');
    await geoResponse;
    await page.getByText('GE',{exact:true}).first().waitFor();
    await page.getByLabel('ქალაქი',{exact:true}).press('ArrowDown');
    await page.getByLabel('ქალაქი',{exact:true}).press('Enter');
    assert.equal((await cityResponse).status(),200);
    const sharedResponse=page.waitForResponse(r=>r.url().includes('/v1/discovery/people?')&&r.url().includes('shared_only=true'));
    await page.getByRole('checkbox',{name:'საერთო ინტერესებით'}).check();
    assert.equal((await sharedResponse).status(),200);
    await page.getByRole('button',{name:'სია',exact:true}).click();
    await page.locator('.discover-list article').first().waitFor();
    assert.equal(await page.locator('.discover-list article').count(),3);
    await page.locator('.discover-list button').first().click(); await ready(page);
    assert(new URL(page.url()).searchParams.get('shared')==='1');
    await page.goto(base+'/discover?q=no-such-wave3-person');
    await page.getByRole('heading',{name:'ჯერ ვერავინ მოიძებნა'}).waitFor();
    pass('Server shared-interest filter, browsable list-to-deck and honest empty state');
    await page.goto(base+'/discover'); await page.locator('.discover-swipe-card').waitFor();
    const firstPage=(await api(page,'/v1/discovery/people')).data;
    assert(firstPage.next_cursor,'local QA expects enough eligible profiles for two pages');
    const pagedResponse=page.waitForResponse(r=>r.url().includes('/v1/discovery/people?')&&r.url().includes('after='));
    for(let i=0;i<12;i++) {
      const before=await page.locator('.discover-swipe-card').getAttribute('data-person-id');
      await page.getByRole('button',{name:'შემდეგი ადამიანი',exact:true}).click();
      await page.waitForFunction(id=>document.querySelector('.discover-swipe-card')?.dataset.personId!==id,before);
    }
    assert.equal((await pagedResponse).status(),200);
    assert(!firstPage.items.some(p=>p.id===new URL(page.url()).searchParams.get('person')));
    pass('Next crosses the 12-person boundary using a real cursor request without a full feed');
    await page.goto(base+'/discover?'+query); await ready(page);
    await context.setOffline(true);
    await page.locator('#people-search').fill('offline-wave3');
    await page.getByRole('button',{name:'ძებნა',exact:true}).click();
    await page.getByText('პროფილები ვერ ჩაიტვირთა.',{exact:true}).waitFor({timeout:20000});
    await context.setOffline(false);
    await page.getByRole('button',{name:'ხელახლა ცდა',exact:true}).click();
    await page.getByRole('heading',{name:'ჯერ ვერავინ მოიძებნა'}).waitFor();
    pass('Actual offline API failure renders retry; restored network recovers');
    // Real touch events with native vertical pan, plus reduced-motion preference.
    const touchContext=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true,reducedMotion:'reduce',storageState:await context.storageState()});
    const touch=await touchContext.newPage(); await touch.goto(base+'/discover?'+query); await ready(touch);
    const cdp=await touchContext.newCDPSession(touch);
    async function touchDrag(dx,dy) {
      const b=await touch.locator('.discover-photo').boundingBox(); const x=b.x+b.width/2,y=b.y+b.height/2;
      await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
      for(let i=1;i<=10;i++) await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x+dx*i/10,y:y+dy*i/10}]});
      await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    }
    const initial=await touch.locator('.discover-swipe-card').getAttribute('data-person-id');
    await touchDrag(0,-100);
    assert.equal(await touch.locator('.discover-swipe-card').getAttribute('data-person-id'),initial);
    await touch.evaluate(()=>scrollTo(0,0)); await touchDrag(-100,0);
    await touch.waitForFunction(id=>document.querySelector('.discover-swipe-card')?.dataset.personId!==id,initial);
    await touchDrag(100,0);
    await touch.locator('dialog[open]').waitFor();
    await touch.getByRole('button',{name:'ჯერ არა',exact:true}).click();
    assert.equal(await touch.locator('.discover-photo').evaluate(el=>getComputedStyle(el).transitionDuration),'0s');
    await touch.screenshot({path:`${out}/touch-reduced-motion.png`});
    pass('Native touch vertical scrolling does not navigate; left advances and right confirms/cancels with reduced motion');
    const conn=(await api(page,'/v1/connections')).data.find(c=>[c.user_a_id,c.user_b_id].includes(target.id)&&c.status==='accepted');
    assert.equal((await api(page,`/v1/connections/${conn.id}/transition`,'POST',{action:'block'})).status,200);
    await page.goto(base+'/discover?'+query); await ready(page);
    assert.notEqual(await page.locator('.discover-swipe-card').getAttribute('data-person-id'),target.id);
    assert.equal((await api(other,`/v1/profiles/${accounts[0].id}`)).status,404);
    assert.equal((await api(other,`/v1/profiles/${accounts[0].id}/photos`)).status,404);
    pass('Block removes candidate and denies reverse profile/media access with privacy-safe 404');
    assert.deepEqual(evidence.pageErrors,[]);
    fs.writeFileSync(`${out}/browser-evidence.json`,JSON.stringify(evidence,null,2));
    console.log(JSON.stringify({checks:evidence.checks.length,pageErrors:evidence.pageErrors.length,measurements:evidence.measurements},null,2));
  } finally { await browser.close(); }
})().catch(e=>{ console.error(e); process.exitCode=1; });
