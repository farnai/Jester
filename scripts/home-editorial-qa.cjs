// Real local Chrome/Auth/API. Failure routes abort requests, never fabricate data.
// Setup/cleanup: python -m scripts.prepare_social_profile_qa --wave4 [--cleanup]
const { chromium } = require('playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const accounts = JSON.parse(fs.readFileSync('scratch/wave4-accounts.json', 'utf8'));
const out = process.env.JESTER_QA_OUTPUT || '.jester/reports/verification/home-editorial';
const base = 'http://127.0.0.1:3001';
const evidence = { checks: [], layouts: [], pageErrors: [] };
fs.mkdirSync(out, { recursive: true });
function pass(name) { evidence.checks.push(name); console.log('PASS:', name); }
async function login(page, account) {
  await page.goto(base + '/auth/login');
  await page.locator('#login-email').fill(account.email);
  await page.locator('#login-password').fill(account.password);
  await page.locator('.login-submit').click();
  await page.waitForURL(u => !u.pathname.startsWith('/auth'));
}
async function api(page, path, method = 'GET', body) {
  return page.evaluate(async ({ path, method, body }) => {
    const key = Object.keys(localStorage).find(k => k.endsWith('-auth-token'));
    const session = JSON.parse(localStorage.getItem(key));
    const r = await fetch('http://127.0.0.1:8000' + path, {
      method, headers: { Authorization: 'Bearer ' + session.access_token, 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    return { status: r.status, data: await r.json() };
  }, { path, method, body });
}
async function ready(page) {
  await page.locator('.home-editorial-hero').waitFor();
  await page.waitForFunction(() => !document.querySelector('.home-skeleton'));
  await page.evaluate(() => document.fonts.ready);
}
async function shot(page, name) {
  await page.screenshot({ path: `${out}/${name}.png`, fullPage: true });
}
(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    const a = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const b = await browser.newPage();
    a.on('pageerror', e => evidence.pageErrors.push(e.message));
    await login(a, accounts[0]); await login(b, accounts[1]);
    await ready(a);
    assert.equal(await a.locator('.home-conversation-invitation a').getAttribute('href'), '/discover');
    pass('Unconnected account invitation routes to Discover, never a stranger chat');
    let c = (await api(a, '/v1/connections')).data.find(c => [c.user_a_id, c.user_b_id].includes(accounts[1].id));
    if (!c) {
      const requested = await api(a, '/v1/connections', 'POST', { target_user_id: accounts[1].id });
      assert.equal(requested.status, 201); c = requested.data;
    }
    if (c.status === 'pending') assert.equal((await api(b, `/v1/connections/${c.id}/transition`, 'POST', { action: 'accept' })).status, 200);
    await a.reload(); await ready(a);
    await a.locator(`.home-active-people a[href="/people/${accounts[1].id}"]`).waitFor();
    await a.waitForFunction(() => document.querySelector('.home-active-people img')?.getAttribute('src')?.startsWith('blob:'));
    assert.equal(await a.locator('.home-conversation-invitation a').getAttribute('href'), '/messages');
    pass('Real accepted connection, private portrait and Messages invitation survive reload');
    await a.locator('.home-insight-more > summary').click();
    assert(await a.getByRole('button', { name: 'დააკოპირე აზრი', exact: true }).isVisible());
    await a.locator('.home-insight-context summary').click();
    assert(await a.locator('.home-insight-context p').isVisible());
    await a.locator('.home-insight-more > summary').click();
    assert.equal(await a.getByRole('button', { name: 'დააკოპირე აზრი', exact: true }).isVisible(), false);
    pass('Insight details expand to expose copy and provenance, then collapse without losing content');
    await a.locator('.home-filter button').nth(1).click();
    for (const width of [1440, 1280, 768, 390, 360]) {
      await a.setViewportSize({ width, height: width > 768 ? 1000 : 844 });
      await a.evaluate(() => scrollTo(0, 0));
      await a.waitForTimeout(400);
      const layout = await a.evaluate(() => ({
        width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
        heroCtaHeight: document.querySelector('.home-hero-copy .home-primary-link').getBoundingClientRect().height,
        quickTargets: [...document.querySelectorAll('.home-quick-actions > a')].map(e => e.getBoundingClientRect().height),
        navTargets: [...document.querySelectorAll('.home-mobile-tab')].map(e => e.getBoundingClientRect().height),
        portraitLoaded: document.querySelector('.home-hero-portrait').naturalWidth > 0,
      }));
      assert(layout.scrollWidth <= width, `Overflow at ${width}`);
      assert(layout.heroCtaHeight >= 44);
      assert(layout.quickTargets.every(h => h >= 44));
      if (width <= 768) assert(layout.navTargets.every(h => h >= 44));
      assert(layout.portraitLoaded);
      evidence.layouts.push(layout);
      await shot(a, `home-${width}`);
      if (width === 1440 || width === 390) await a.screenshot({ path: `${out}/home-${width}-viewport.png` });
      if (width === 390 || width === 360) {
        await a.evaluate(() => scrollTo(0, document.querySelector('#home-people').getBoundingClientRect().top + scrollY - 85));
        await a.screenshot({ path: `${out}/discovery-${width}-viewport.png` });
        await a.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
        const clearance = await a.evaluate(() => ({
          width: innerWidth,
          profileActionBottom: document.querySelector('.home-closing a').getBoundingClientRect().bottom,
          navigationTop: document.querySelector('.home-mobile-navigation').getBoundingClientRect().top,
        }));
        assert(clearance.profileActionBottom < clearance.navigationTop, 'Closing profile action obstructed by bottom navigation');
        evidence.layouts.push(clearance);
        await a.screenshot({ path: `${out}/footer-${width}-viewport.png` });
      }
    }
    pass('Five viewport sizes: no horizontal overflow; primary, quick actions and mobile navigation >=44px');
    for (const selector of ['.home-hero-copy a', '.home-quick-actions a:nth-child(3)', '.home-conversation-invitation a', '.home-person h3 a']) {
      const href = await a.locator(selector).first().getAttribute('href');
      await a.locator(selector).first().click();
      await a.waitForURL(u => u.pathname === href);
      await a.goto(base); await ready(a);
    }
    pass('Hero, Connections, Messages and real person navigation resolve');
    await a.route('**/v1/interpretations/daily-energy?*', r => r.abort());
    await a.reload(); await ready(a);
    await a.getByText('დაკვირვება ვერ ჩაიტვირთა', { exact: true }).waitFor();
    assert(await a.locator('.home-active-people li').count() > 0);
    await shot(a, 'home-daily-error-360');
    await a.unroute('**/v1/interpretations/daily-energy?*');
    await a.locator('#home-daily').getByRole('button', { name: /ხელახლა ცდა/ }).click();
    await a.getByText('დაკვირვება ვერ ჩაიტვირთა', { exact: true }).waitFor({ state: 'hidden' });
    pass('Daily request failure stays local; retry restores real content');
    assert.equal(evidence.pageErrors.length, 0);
    pass('No uncaught browser exceptions');
  } finally {
    fs.writeFileSync(`${out}/browser-evidence.json`, JSON.stringify(evidence, null, 2));
    await browser.close();
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
