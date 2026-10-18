// Live services only. Accounts created by prepare_social_profile_qa.py.
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const accounts = JSON.parse(fs.readFileSync('scratch/wave2-accounts.json', 'utf8'));
const out = process.env.JESTER_QA_OUTPUT || '.jester/reports/verification/wave2-social';
fs.mkdirSync(out, { recursive: true });
const base = process.env.JESTER_URL || 'http://127.0.0.1:3001';

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const errors = [];
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  page.on('dialog', dialog => dialog.accept());
  async function login(account) {
    await page.goto(base + '/auth/login');
    await page.locator('#login-email').fill(account.email);
    await page.locator('#login-password').fill(account.password);
    await page.locator('.login-submit').click();
    await page.waitForURL(url => !url.pathname.startsWith('/auth'), { timeout: 30000 });
    await page.goto(base + '/me');
    await page.locator('.social-story h1').waitFor();
  }
  async function api(route, method = 'GET', body) {
    return page.evaluate(async ({ route, method, body }) => {
      const key = Object.keys(localStorage).find(key => key.endsWith('-auth-token'));
      const session = JSON.parse(localStorage.getItem(key));
      const result = await fetch('http://127.0.0.1:8000' + route, {
        method, headers: { Authorization: 'Bearer ' + session.access_token, 'Content-Type': 'application/json' },
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      return { status: result.status, data: await result.json() };
    }, { route, method, body });
  }
  await login(accounts[0]);
  const existing = await api(`/v1/profiles/${accounts[0].id}/photos`);
  for (const photo of existing.data) await api(`/v1/profiles/me/photos/${photo.id}`, 'DELETE');
  await page.reload();
  await page.getByText('ფოტო ჯერ არ არის', { exact: true }).waitFor();
  await page.screenshot({ path: `${out}/empty-profile.png` });
  await page.getByRole('button', { name: /ფოტოების მართვა/ }).click();
  for (let index = 0; index < 6; index++) {
    const uploaded = page.waitForResponse(r => r.url().endsWith('/v1/profiles/me/photos') && r.request().method() === 'POST');
    const file = index % 2 ? 'hero_woman_highres.jpg' : 'hero_portrait.jpg';
    await page.getByLabel('ფოტოს დამატება', { exact: true }).setInputFiles(path.join('frontend/src/assets/registration', file));
    assert.equal((await uploaded).status(), 201);
    await page.waitForFunction(n => document.querySelectorAll('.social-photo-row').length === n, index + 1);
  }
  assert.equal(await page.getByLabel('ფოტოს დამატება', { exact: true }).isDisabled(), true);
  await page.getByRole('button', { name: 'მთავარ ფოტოდ 2', exact: true }).click();
  await page.waitForTimeout(350);
  const before = (await api(`/v1/profiles/${accounts[0].id}/photos`)).data;
  await page.getByRole('button', { name: 'უკან 2', exact: true }).click();
  await page.waitForTimeout(350);
  assert.notEqual((await api(`/v1/profiles/${accounts[0].id}/photos`)).data[1].id, before[1].id);
  await page.getByRole('button', { name: 'წაშლა 6', exact: true }).click();
  await page.waitForFunction(() => document.querySelectorAll('.social-photo-row').length === 5);
  await page.reload();
  await page.locator('.social-portrait img').waitFor();
  assert.equal((await api(`/v1/profiles/${accounts[0].id}/photos`)).data.length, 5);

  await page.locator('.social-interests').getByRole('button', { name: 'რედაქტირება', exact: true }).click();
  await page.getByRole('button', { name: 'გასუფთავება', exact: true }).click();
  const pills = page.locator('.social-interest-editor .social-tags button');
  await pills.first().waitFor();
  for (let i = 0; i < 3; i++) await pills.nth(i).click();
  await page.getByRole('button', { name: 'ინტერესების შენახვა', exact: true }).click();
  await page.getByText('ინტერესები შენახულია.', { exact: true }).waitFor();
  assert.equal((await api('/v1/interests/me')).data.interest_ids.length, 3);

  const measurements = [];
  async function capture(surface) {
    for (const [width, height] of [[1440,900],[1280,800],[390,844],[320,700]]) {
      await page.setViewportSize({ width, height });
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(250);
      const measure = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth, font: getComputedStyle(document.querySelector('h1')).fontFamily, loadedImages: [...document.querySelectorAll('.social-identity img')].every(i => i.complete && i.naturalWidth > 0) }));
      measurements.push({ surface, height, ...measure });
      await page.screenshot({ path: `${out}/${surface}-${width}x${height}.png` });
      if (width === 1440 || width === 320) await page.screenshot({ path: `${out}/${surface}-${width}-full.png`, fullPage: true });
    }
  }
  await capture('me');
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.getByRole('button', { name: 'გასვლა', exact: true }).last().click();
  await login(accounts[0]);
  assert.equal((await api(`/v1/profiles/${accounts[0].id}/photos`)).data.length, 5);
  assert.equal((await api('/v1/interests/me')).data.interest_ids.length, 3);
  await page.getByRole('button', { name: 'გასვლა', exact: true }).last().click();
  await login(accounts[1]);
  await page.goto(base + '/people/' + accounts[0].id);
  await page.locator('.social-portrait img').waitFor();
  await page.getByText('2 საერთო ინტერესი', { exact: true }).waitFor();
  await capture('person');
  assert.equal((await api(`/v1/profiles/me/photos/${before[0].id}`, 'DELETE')).status, 404);
  await page.goto(base + '/');
  await page.locator('.home-shell').waitFor();
  await page.screenshot({ path: `${out}/home-regression.png` });
  const connection = await api('/v1/connections', 'POST', { target_user_id: accounts[0].id });
  assert.equal(connection.status, 201);
  assert.equal((await api(`/v1/connections/${connection.data.id}/transition`, 'POST', { action: 'block' })).status, 200);
  assert.equal((await api(`/v1/profiles/${accounts[0].id}/photos`)).status, 404);
  assert.equal((await api(`/v1/interests/people/${accounts[0].id}`)).status, 404);
  await page.goto(base + '/people/' + accounts[0].id);
  await page.getByText('პროფილი ვერ მოიძებნა ან მიუწვდომელია.', { exact: true }).waitFor();
  await page.screenshot({ path: `${out}/blocked-profile.png` });
  assert.equal(await page.locator('.social-identity').count(), 0);
  await api(`/v1/connections/${connection.data.id}/transition`, 'POST', { action: 'unblock' });
  fs.writeFileSync(`${out}/browser-results.json`, JSON.stringify({ liveServices: true, measurements, pageErrors: errors, flows: ['empty profile', 'six uploads', 'disabled seventh', 'primary', 'reorder', 'delete', 'reload', 'interests edit', 'logout/login persistence', 'person profile', 'common interests', 'unauthorized delete', 'Home navigation', 'blocked profile hides gallery and interests'] }, null, 2));
  assert.equal(errors.length, 0, errors.join('\n'));
  assert(measurements.every(m => m.scrollWidth <= m.width), 'Horizontal overflow found; inspect screenshots');
  assert(measurements.every(m => m.loadedImages), 'Image loading failure');
  await browser.close();
  console.log('Live browser QA passed at all four viewports. Screenshots and measurements saved.');
})().catch(error => { console.error(error); process.exit(1); });
