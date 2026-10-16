// Browser integration checks with intercepted auth/API responses. No real account is created.
const { chromium } = require(process.env.JESTER_PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.JESTER_QA_URL || 'http://127.0.0.1:3001';
const output = process.env.JESTER_QA_OUTPUT || '.jester/reports/verification/registration-fidelity';
const user = { id: '00000000-0000-4000-8000-000000000123', email: 'visual-qa@example.invalid', aud: 'authenticated', role: 'authenticated', identities: [{ provider: 'email' }], app_metadata: {}, user_metadata: {}, created_at: '2026-10-16T00:00:00Z' };
const profile = { id: user.id, onboarding_completed: false, onboarding_step: 1, first_name: null, last_name: null, display_name: null };
const encode = value => Buffer.from(JSON.stringify(value)).toString('base64url');
const accessToken = `${encode({ alg: 'HS256', typ: 'JWT' })}.${encode({ sub: user.id, role: 'authenticated', exp: Math.floor(Date.now() / 1000) + 3600 })}.browser-mock-only`;
const session = { access_token: accessToken, refresh_token: 'browser-mock-only', token_type: 'bearer', expires_in: 3600, user };

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ channel: process.env.JESTER_QA_BROWSER || 'msedge', headless: true });
  const results = [];
  try {
    for (const width of [1440, 390, 320]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      let mode = 'error';
      let authCalls = 0;
      let initializeCalls = 0;
      let release;
      let gate = Promise.resolve();
      let submitted;
      await page.route('**/*', async route => {
        const pathname = new URL(route.request().url()).pathname;
        const json = (body, status = 200) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
        if (pathname.startsWith('/auth/v1/')) {
          if (pathname.endsWith('/signup')) {
            authCalls++;
            submitted = route.request().postDataJSON();
            await gate;
            if (mode === 'duplicate') return json({ msg: 'User already registered', code: 'user_already_exists' }, 422);
            if (mode === 'unconfirmed') return json({ ...user, identities: [{ provider: 'email' }] });
            if (mode === 'success') return json(session);
            return json({ msg: 'Registration unavailable for QA', code: 'unexpected_failure' }, 400);
          }
          if (pathname.endsWith('/token')) return json({ msg: 'Email not confirmed', code: 'email_not_confirmed' }, 400);
          if (pathname.endsWith('/user')) return json(user);
          return json({});
        }
        if (pathname.startsWith('/v1/')) {
          if (pathname.endsWith('/profiles/initialize')) { initializeCalls++; return json(profile); }
          if (pathname.endsWith('/profiles/me')) return initializeCalls ? json(profile) : json({ error: { code: 'not_found', message: 'Profile not initialized' } }, 404);
          return json({ has_birth_data: false, items: [] });
        }
        await route.continue();
      });
      await page.goto(`${base}/auth/register`);
      const email = page.locator('#registration-email');
      const password = page.locator('#registration-password');
      const confirm = page.locator('#registration-confirm-password');
      const submit = page.locator('button[type=submit]');
      await submit.click();
      assert.equal(authCalls, 0);
      assert.equal(await email.evaluate(el => el.validity.valueMissing), true);
      await email.fill('invalid');
      assert.equal(await email.evaluate(el => el.validity.typeMismatch), true);
      await email.fill(user.email);
      await password.fill('short');
      await confirm.fill('short');
      await submit.click();
      assert.equal(authCalls, 0);
      await password.fill('visual-qa-password');
      await confirm.fill('not-the-same');
      await submit.click();
      await page.getByRole('alert').waitFor();
      assert.match(await page.getByRole('alert').innerText(), /პაროლები არ ემთხვევა/);
      assert.equal(authCalls, 0);
      await page.getByRole('button', { name: 'პაროლის ჩვენება', exact: true }).click();
      assert.equal(await password.getAttribute('type'), 'text');
      await page.getByRole('button', { name: 'პაროლის დამალვა', exact: true }).click();
      assert.equal(await password.getAttribute('type'), 'password');
      await page.getByRole('button', { name: 'გამეორებული პაროლის ჩვენება', exact: true }).click();
      assert.equal(await confirm.getAttribute('type'), 'text');
      await page.getByRole('button', { name: 'გამეორებული პაროლის დამალვა', exact: true }).click();
      assert.equal(await confirm.getAttribute('type'), 'password');
      await confirm.fill('visual-qa-password');
      gate = new Promise(resolve => { release = resolve; });
      await submit.click();
      assert.equal(await submit.isDisabled(), true);
      assert.equal(await page.locator('form').getAttribute('aria-busy'), 'true');
      release();
      await page.getByRole('alert').filter({ hasText: 'Registration unavailable for QA' }).waitFor();
      assert.equal(await submit.isEnabled(), true);
      assert.equal(submitted.email, user.email);
      assert.equal(submitted.password, 'visual-qa-password');
      mode = 'duplicate';
      await submit.click();
      await page.getByRole('alert').filter({ hasText: 'ეს ელფოსტა უკვე რეგისტრირებულია' }).waitFor();
      assert.equal(await page.getByRole('button', { name: 'პაროლის აღდგენა', exact: true }).isVisible(), true);
      await page.screenshot({ path: `${output}/functional-error-${width}.png`, fullPage: true });
      mode = 'unconfirmed';
      await submit.click();
      await page.waitForURL('**/auth/verify-email');
      results.push({ width, checks: 'required/email/min-length/mismatch, both visibility controls, loading, payload, server error, duplicate actions: PASS', emailVerification: 'Pending confirmation routes to verification with no password login attempt.' });
      await page.getByRole('link', { name: 'შესვლა', exact: true }).click();
      await page.waitForURL('**/auth/login');
      await page.goto(`${base}/auth/register`);
      if (width < 761) {
        await page.getByRole('button', { name: 'მენიუ', exact: true }).click();
        assert.equal(await page.getByRole('button', { name: 'მენიუ', exact: true }).getAttribute('aria-expanded'), 'true');
        await page.locator('.registration-mobile-login').click();
        await page.waitForURL('**/auth/login');
        await page.goto(`${base}/auth/register`);
      }
      mode = 'success';
      await email.fill(user.email);
      await password.fill('visual-qa-password');
      await confirm.fill('visual-qa-password');
      await submit.click();
      await page.waitForURL('**/onboarding/birth-data');
      assert.equal(initializeCalls, 1);
      results[results.length - 1].navigation = 'Login and mocked registration → profile initialization → onboarding/birth-data: PASS';
      await page.close();
    }
    fs.mkdirSync(output, { recursive: true });
    fs.writeFileSync(`${output}/functional-results.json`, JSON.stringify({ backend: 'MOCKED; no live signup/email delivery claim', results }, null, 2));
    console.log(JSON.stringify(results, null, 2));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
