// Run from the repository root. Playwright is a QA tool, not an app dependency.
// Set JESTER_PLAYWRIGHT_MODULE to an installed playwright package if not on NODE_PATH.
const { chromium } = require(process.env.JESTER_PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const assert = require('node:assert/strict');
const base = process.env.JESTER_QA_URL || 'http://127.0.0.1:3001';
const pass = process.env.JESTER_QA_PASS || 'final';
const output = path.join('.jester/reports/verification/registration-fidelity', pass);
const sizes = [[1440, 900], [1280, 800], [430, 932], [390, 844], [360, 800], [320, 700]];

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ channel: process.env.JESTER_QA_BROWSER || 'msedge', headless: true });
  const results = [];
  try {
    for (const [width, height] of sizes) {
      const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(`${base}/auth/register`);
      await page.evaluate(async () => {
        await document.fonts.ready;
        await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
      });
      const geometry = await page.evaluate(() => {
        const box = selector => {
          const { x, y, width, height } = document.querySelector(selector).getBoundingClientRect();
          return { x, y, width, height };
        };
        const scene = document.querySelector('.registration-composition').getBoundingClientRect();
        const header = document.querySelector('.registration-header').getBoundingClientRect();
        const uiWidth = scene.width;
        const uiHeight = scene.bottom - header.top;
        const normalize = rect => ({ x: (rect.x - scene.x) / uiWidth, y: (rect.y - header.top) / uiHeight, width: rect.width / uiWidth, height: rect.height / uiHeight });
        const selectors = { logo: '.registration-brand', navigation: '.registration-navigation', headline: 'h1', card: '.registration-card', feature1: '.registration-feature:nth-child(1)', feature2: '.registration-feature:nth-child(2)', feature3: '.registration-feature:nth-child(3)', portraitImage: '.registration-portrait img', panorama: '.registration-panorama', annotation: '.registration-annotation' };
        return {
          uiWidth, uiHeight, uiAspectRatio: uiWidth / uiHeight,
          landmarks: Object.fromEntries(Object.entries(selectors).map(([name, selector]) => [name, normalize(box(selector))])),
          overflow: document.documentElement.scrollWidth > innerWidth,
          heading: box('h1'), card: box('.registration-card'), portrait: box('.registration-portrait'),
          brokenImages: [...document.images].filter(img => !img.naturalWidth).map(img => img.getAttribute('src')),
          formCount: document.forms.length,
          inputSizes: [...document.querySelectorAll('input')].map(input => ({ width: input.clientWidth, height: input.clientHeight })),
          clippedControls: [...document.querySelectorAll('.registration-input input, .registration-input button')].some(control => {
            const child = control.getBoundingClientRect();
            const parent = control.parentElement.getBoundingClientRect();
            return child.left < parent.left || child.right > parent.right + 1 || child.top < parent.top || child.bottom > parent.bottom + 1;
          }),
          mobileInputFontSizes: [...document.querySelectorAll('input')].map(input => parseFloat(getComputedStyle(input).fontSize)),
        };
      });
      assert.equal(geometry.overflow, false, `Overflow at ${width}`);
      assert.deepEqual(geometry.brokenImages, []);
      assert.equal(geometry.formCount, 1);
      assert.equal(geometry.clippedControls, false);
      assert(geometry.inputSizes.every(input => input.height >= 44 && input.width >= 140));
      if (width <= 430) assert(geometry.mobileInputFontSizes.every(size => size >= 16));
      assert.deepEqual(errors, []);
      await page.screenshot({ path: path.join(output, `${width}x${height}.png`) });
      await page.screenshot({ path: path.join(output, `${width}x${height}-full.png`), fullPage: true });
      results.push({ width, height, ...geometry, errors });
      await page.close();
    }
    fs.writeFileSync(path.join(output, 'geometry.json'), JSON.stringify(results, null, 2));
    if (pass === 'final') {
      const comparison = await browser.newPage({ viewport: { width: 1280, height: 900 } });
      await comparison.goto(pathToFileURL(path.resolve(output, '../comparison.html')).href);
      await comparison.evaluate(() => Promise.all([...document.images].map(img => img.decode())));
      await comparison.locator('#desktop').screenshot({ path: path.join(output, '../desktop-comparison-corrected.png') });
      await comparison.locator('#mobile').screenshot({ path: path.join(output, '../mobile-comparison-corrected.png') });
      await comparison.locator('#desktop-before-after').screenshot({ path: path.join(output, '../desktop-before-after.png') });
      await comparison.locator('#mobile-before-after').screenshot({ path: path.join(output, '../mobile-before-after.png') });
      await comparison.close();
    }
    console.log(JSON.stringify(results, null, 2));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
