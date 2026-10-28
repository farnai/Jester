// Real local Chrome/Auth/API verification for rebuilt JESTER Authenticated Home.
// Failure routes abort requests, never fabricate data.
// Setup/cleanup: python -m scripts.prepare_social_profile_qa --wave4 [--cleanup]
const { chromium } = require('playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');

const accounts = JSON.parse(fs.readFileSync('scratch/wave4-accounts.json', 'utf8'));
const out = process.env.JESTER_QA_OUTPUT || '.jester/reports/verification/home-editorial';
const base = process.env.JESTER_BASE_URL || 'http://127.0.0.1:3001';
const apiBase = process.env.JESTER_API_URL || 'http://127.0.0.1:8000';
const evidence = { checks: [], layouts: [], pageErrors: [] };
fs.mkdirSync(out, { recursive: true });

function pass(name) {
  evidence.checks.push(name);
  console.log('PASS:', name);
}

async function login(page, account) {
  await page.goto(base + '/auth/login');
  await page.locator('#login-email').fill(account.email);
  await page.locator('#login-password').fill(account.password);
  await page.locator('.login-submit').click();
  await page.waitForURL((u) => !u.pathname.startsWith('/auth'));
}

async function api(page, path, method = 'GET', body) {
  return page.evaluate(
    async ({ apiBase, path, method, body }) => {
      const key = Object.keys(localStorage).find((k) => k.endsWith('-auth-token'));
      const session = JSON.parse(localStorage.getItem(key));
      const r = await fetch(apiBase + path, {
        method,
        headers: {
          Authorization: 'Bearer ' + session.access_token,
          'Content-Type': 'application/json',
        },
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      return { status: r.status, data: await r.json() };
    },
    { apiBase, path, method, body }
  );
}

async function ready(page) {
  await page.locator('.home-salon-masthead').waitFor();
  await page.waitForFunction(() => !document.querySelector('.home-skeleton'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => {
    const frames = [...document.querySelectorAll('.home-candidate-media')].filter(
      (el) => el.offsetParent !== null
    );
    return (
      frames.length === 0 ||
      frames.every((f) => {
        if (f.querySelector('.home-portrait-poster')) return true;
        const img = f.querySelector('img');
        return Boolean(img && img.complete && img.naturalWidth > 0);
      })
    );
  });
}

async function shot(page, name) {
  await page.screenshot({ path: `${out}/${name}.png`, fullPage: true });
}

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    const a = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const b = await browser.newPage();
    a.on('pageerror', (e) => evidence.pageErrors.push(e.message));

    await login(a, accounts[0]);
    await login(b, accounts[1]);
    await ready(a);

    assert.equal(await a.locator('.home-editorial-hero').count(), 0);
    assert.equal(await a.locator('.home-quick-actions').count(), 0);
    pass('Obsolete public landing hero and duplicate quick-action strip are removed');

    assert.equal(
      await a.locator('.home-conversation-invitation a.home-primary-link').getAttribute('href'),
      '/discover'
    );
    pass('Unconnected account invitation routes to Discover, never a stranger chat');

    let c = (await api(a, '/v1/connections')).data.find((item) =>
      [item.user_a_id, item.user_b_id].includes(accounts[1].id)
    );
    if (!c) {
      const requested = await api(a, '/v1/connections', 'POST', {
        target_user_id: accounts[1].id,
      });
      assert.equal(requested.status, 201);
      c = requested.data;
    }
    if (c.status === 'pending') {
      assert.equal(
        (await api(b, `/v1/connections/${c.id}/transition`, 'POST', { action: 'accept' })).status,
        200
      );
    }

    await a.reload();
    await ready(a);
    await a.locator(`.home-active-people a[href="/people/${accounts[1].id}"]`).waitFor();
    assert.equal(
      await a.locator('.home-conversation-invitation a.home-primary-link').getAttribute('href'),
      '/messages'
    );
    pass('Real accepted connection, active circle and Messages invitation survive reload');

    await a.locator('.home-insight-context summary').click();
    assert(await a.locator('.home-insight-context p').isVisible());
    await a.getByRole('tab', { name: 'საუბარი' }).click();
    await a.getByRole('tab', { name: 'შენი ვერდიქტი' }).click();
    await a.getByRole('tab', { name: 'დღის სიმართლე' }).click();
    pass('Spotlight Stage provenance, Truth-Flip and 4-facet ME Atelier switch cleanly');

    await a.locator('.home-filter button').nth(1).click();

    for (const width of [1440, 1280, 768, 390, 360, 320]) {
      await a.setViewportSize({ width, height: width > 768 ? 1000 : 844 });
      await a.evaluate(() => scrollTo(0, 0));
      await a.waitForTimeout(350);
      await ready(a);

      const layout = await a.evaluate(() => {
        const visibleCards = [...document.querySelectorAll('.home-candidate-card')].filter(
          (c) => c.offsetParent !== null
        );
        return {
          width: innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          stageCtaHeight: document
            .querySelector('.home-spotlight-stage .home-cta-orange')
            .getBoundingClientRect().height,
          visibleCardCount: visibleCards.length,
          navTargets: [...document.querySelectorAll('.home-mobile-tab')].map(
            (e) => e.getBoundingClientRect().height
          ),
        };
      });

      assert(layout.scrollWidth <= width, `Overflow at ${width}`);
      assert(layout.stageCtaHeight >= 44);
      if (width < 768) {
        assert.equal(layout.visibleCardCount, 1, `Mobile ${width} must show 1 active candidate card`);
        assert(layout.navTargets.every((h) => h >= 44));
      }
      evidence.layouts.push(layout);
      await shot(a, `home-${width}`);
      if (width === 1440 || width === 390) {
        await a.screenshot({ path: `${out}/home-${width}-viewport.png` });
      }
      if (width === 390 || width === 360 || width === 320) {
        await a.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
        const clearance = await a.evaluate(() => ({
          width: innerWidth,
          profileActionBottom: document
            .querySelector('.home-closing a')
            .getBoundingClientRect().bottom,
          navigationTop: document
            .querySelector('.home-mobile-navigation')
            .getBoundingClientRect().top,
        }));
        assert(
          clearance.profileActionBottom < clearance.navigationTop,
          `Closing profile action obstructed by bottom navigation at ${width}`
        );
        evidence.layouts.push(clearance);
      }
    }
    pass('Six viewport sizes (1440, 1280, 768, 390, 360, 320): zero overflow, single-card mobile deck, >=44px targets');

    await a.setViewportSize({ width: 1440, height: 1000 });
    await ready(a);
    for (const selector of [
      '.home-pill-profile',
      '.home-circle-top a',
      '.home-conversation-invitation a.home-primary-link',
      '.home-candidate-name a',
    ]) {
      const href = await a.locator(selector).first().getAttribute('href');
      await a.locator(selector).first().click();
      await a.waitForURL((u) => u.pathname === href);
      await a.goto(base);
      await ready(a);
    }
    pass('Profile, Connections, Messages and real person navigation resolve');

    await a.route('**/v1/interpretations/daily-energy?*', (r) => r.abort());
    await a.reload();
    await a.locator('.home-salon-masthead').waitFor();
    await a.getByText('დაკვირვება ვერ ჩაიტვირთა', { exact: true }).waitFor();
    assert((await a.locator('.home-active-people li').count()) > 0);
    await shot(a, 'home-daily-error');
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
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
