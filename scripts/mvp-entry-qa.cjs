// Real local Supabase + backend journey. No mocked responses or privileged auth bypass.
// Requires email confirmations, local mail capture, and a running frontend/backend.
const { chromium } = require(process.env.JESTER_PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const base = process.env.JESTER_QA_URL || 'http://127.0.0.1:3001';
const out = '.jester/reports/verification/mvp-entry';
const email = `jester-entry-${Date.now()}@example.test`;
const password = `Qa!${crypto.randomBytes(18).toString('hex')}`;
const checks = [];
const record = name => { checks.push(name); console.log('PASS', name); };

async function confirmationLink() {
  for (let attempt = 0; attempt < 40; attempt++) {
    const response = await fetch('http://127.0.0.1:54324/api/v1/messages');
    const data = await response.json();
    const mail = data.messages?.find(m => m.To?.some(to => to.Address === email));
    if (mail) {
      const full = await (await fetch(`http://127.0.0.1:54324/api/v1/message/${mail.ID}`)).json();
      const link = (full.HTML || full.Text).match(/https?:\/\/[^\s"<>]+\/auth\/v1\/verify[^\s"<>]+/);
      if (link) return link[0].replaceAll('&amp;', '&');
    }
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  throw new Error('Confirmation email not delivered to the local mail server');
}

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  const step = number => page.getByText(`ეტაპი ${number} / 8`, { exact: true }).waitFor();
  const next = () => page.getByRole('button', { name: /შემდეგი/ }).click();
  const shot = name => page.screenshot({ path: path.join(out, `${name}.png`), fullPage: true });
  const session = () => page.evaluate(() => {
    const key = Object.keys(localStorage).find(k => /^sb-.*-auth-token$/.test(k));
    return key ? JSON.parse(localStorage.getItem(key)) : null;
  });
  const api = async (route, method = 'GET', data) => {
    const auth = await session();
    return page.request.fetch(`http://127.0.0.1:8000${route}`, {
      method, data, headers: auth ? { Authorization: `Bearer ${auth.access_token}` } : {},
    });
  };
  try {
    await page.goto(`${base}/onboarding`);
    await page.waitForURL('**/auth/login');
    assert.equal((await api('/v1/profiles/me')).status(), 401);
    record('Unauthenticated UI and API access denied');
    await page.goto(`${base}/auth/register`);
    await page.getByLabel('ელფოსტა', { exact: true }).fill(email);
    await page.getByLabel('პაროლი', { exact: true }).fill(password);
    await page.getByLabel('გაიმეორე პაროლი', { exact: true }).fill(`${password}x`);
    await page.locator('.registration-submit').click();
    await page.getByRole('alert').filter({ hasText: 'პაროლები არ ემთხვევა' }).waitFor();
    await page.getByLabel('გაიმეორე პაროლი', { exact: true }).fill(password);
    await page.locator('.registration-submit').click();
    await page.waitForURL('**/auth/verify-email');
    assert.equal(await session(), null);
    // Local auth.email.max_frequency is 1s; respect the real resend rate limit.
    await page.waitForTimeout(1100);
    await page.getByRole('button', { name: 'წერილის ხელახლა გაგზავნა' }).click();
    await page.getByRole('status').filter({ hasText: 'დადასტურების წერილი გამოგზავნილია' }).waitFor();
    await shot('01-email-verification');
    record('Real signup requires email verification; mismatch validation works');
    await page.getByRole('link', { name: 'შესვლა', exact: true }).click();
    await page.locator('input[type=password]').fill(password);
    await page.locator('button[type=submit]').click();
    await page.waitForURL('**/auth/verify-email');
    assert.equal(await session(), null);
    record('Unconfirmed password login cannot bypass verification');
    await page.goto(await confirmationLink());
    await step(1);
    record('Delivered confirmation link creates real authenticated session');
    await api('/v1/profiles/me', 'PATCH', { is_discoverable: false });
    const bypassDenied = await page.evaluate(async () => {
      const { supabase } = await import('/src/core/realtime/supabase.ts');
      const { data: { user } } = await supabase.auth.getUser();
      const { error } = await supabase.from('profiles').update({ onboarding_completed: true }).eq('id', user.id);
      return error?.code === '42501';
    });
    assert.equal(bypassDenied, true);
    assert.equal((await api('/v1/profiles/me/complete-onboarding', 'POST')).status(), 400);
    assert.equal((await api('/v1/profiles/me', 'PATCH', { onboarding_completed: true })).status(), 400);
    await page.goto(`${base}/`);
    await step(1);
    record('Incomplete onboarding cannot enter Home or complete through backend');
    await page.locator('input[autocomplete=given-name]').fill('MVP');
    await page.locator('input[autocomplete=family-name]').fill('Journey');
    const slowSave = async route => {
      if (route.request().method() === 'PATCH') await new Promise(resolve => setTimeout(resolve, 600));
      await route.continue();
    };
    await page.route('**/v1/profiles/me', slowSave);
    await next();
    await page.locator('fieldset[disabled]').waitFor();
    assert.equal(await page.locator('input[autocomplete=given-name]').isDisabled(), true);
    await step(2);
    await page.unroute('**/v1/profiles/me', slowSave);
    await page.reload(); await step(2);
    record('Identity and step persist after reload');
    // Failure injection aborts transport, never fabricates a successful response.
    await page.route('**/rest/v1/birth_data?*', route => route.abort('failed'));
    await page.reload();
    await page.getByRole('alert').filter({ hasText: 'მონაცემების ჩატვირთვა ვერ მოხერხდა' }).waitFor();
    assert.equal(await page.locator('input[type=date]').count(), 0);
    await page.unroute('**/rest/v1/birth_data?*');
    await page.getByRole('button', { name: 'ხელახლა ცდა' }).click();
    await step(2);
    record('Loading locks controls; failed reads block editing and retry restores persisted progress');
    await page.locator('input[type=date]').fill('1995-05-15');
    await next(); await step(3);
    await page.locator('input[type=radio]').nth(2).check();
    await next(); await step(4);
    await page.goto(`${base}/logout`);
    await page.waitForURL('**/auth/login');
    await page.locator('input[type=email]').fill(email);
    await page.locator('input[type=password]').fill(password);
    await page.locator('button[type=submit]').click();
    await step(4);
    record('Logout/login resumes persisted birth date and unknown-time step');
    const city = page.locator('input[type=text]');
    await city.fill('Tbilisi');
    await page.getByText('Tbilisi', { exact: true }).first().click();
    await next(); await step(5);
    await page.getByRole('button', { name: /დიახ/ }).click();
    await next(); await step(6);
    await page.getByRole('button', { name: /გამოტოვ/ }).click(); await step(7);
    await page.getByRole('button', { name: /უკან/ }).click(); await step(6);
    const chips = page.getByRole('button', { name: /^\+ / });
    for (let index = 0; index < 3; index++) await chips.first().click();
    await next(); await step(7);
    await page.getByRole('button', { name: /გამოტოვ/ }).click(); await step(8);
    await page.reload(); await step(8);
    await shot('02-onboarding-resumed');
    record('Canonical places and optional skips persist; final review resumes');
    await page.getByRole('button', { name: /დასრულება და შესვლა/ }).click();
    await page.waitForURL(base + '/');
    await page.getByRole('heading', { name: 'MVP J.' }).waitFor();
    const profile = await (await api('/v1/profiles/me')).json();
    assert.equal(profile.onboarding_completed, true);
    assert.ok(profile.current_city_id);
    assert.equal((await (await api('/v1/interests/me')).json()).interest_ids.length, 3);
    assert.equal(await page.evaluate(async () => {
      const { API } = await import('/src/core/api/endpoints.ts');
      const { supabase } = await import('/src/core/realtime/supabase.ts');
      const { data: { user } } = await supabase.auth.getUser();
      const birth = await API.astrology.getBirthData(user.id);
      return birth.birth_date === '1995-05-15' && birth.birth_time === null && birth.birth_time_precision === 'unknown' && !!birth.birth_city_id;
    }), true);
    assert.equal((await api('/v1/astrology/profile/safe-astro')).status(), 200);
    await shot('03-home-desktop');
    await page.goto(`${base}/onboarding`);
    await page.waitForURL(base + '/');
    await page.reload();
    await page.getByRole('heading', { name: 'MVP J.' }).waitFor();
    await page.setViewportSize({ width: 390, height: 844 });
    await shot('04-home-mobile');
    record('Completion persists, reaches Home, and completed users cannot re-enter onboarding');
    await page.route('**/v1/profiles/me', route => route.abort('failed'));
    await page.reload();
    await page.getByRole('alert').filter({ hasText: 'პროფილის ჩატვირთვა ვერ მოხერხდა' }).waitFor();
    await page.unroute('**/v1/profiles/me');
    await page.getByRole('button', { name: 'ხელახლა ცდა' }).click();
    await page.getByRole('heading', { name: 'MVP J.' }).waitFor();
    record('Profile outage has retry recovery without restarting onboarding');
    await page.goto(`${base}/logout`);
    await page.waitForURL('**/auth/login');
    await page.goto(`${base}/auth/callback#error=access_denied&error_description=Expired`);
    await page.getByRole('heading', { name: 'ავტორიზაციის შეცდომა' }).waitFor();
    await page.getByRole('link', { name: 'დადასტურების წერილის ხელახლა გაგზავნა' }).waitFor();
    record('Expired confirmation callback offers recovery instead of infinite loading');
    fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify({ environment: 'local Supabase, real email capture and backend; no API mocks', checks }, null, 2));
  } catch (error) {
    await shot('failure');
    console.error(error.message.replace(/https?:\/\/\S+/g, '[URL]'));
    console.log('Page:', await page.locator('body').innerText());
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
})();
