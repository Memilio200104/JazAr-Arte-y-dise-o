const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage();
    for (const [width, height] of [[1920, 1080], [1536, 728], [1280, 650]]) {
      await page.setViewportSize({ width, height });
      await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle' });
      assert.equal(await page.locator('.process-scene').isVisible(), true, `${width}x${height}: scene missing`);
      for (const step of ['2', '4', '3']) {
        await page.locator(`#paso-${step}`).evaluate(el => el.scrollIntoView({ block: 'center', behavior: 'instant' }));
        await page.waitForFunction(n => document.querySelector('#process-number').textContent === `0${n}`, step);
        await page.waitForFunction(n => [...document.querySelectorAll('[data-frame]')].every(layer => Number(getComputedStyle(layer).opacity) === (layer.dataset.frame === n ? 1 : 0)), step);
        const box = await page.locator('.process-scene').boundingBox();
        assert.ok(box.y >= 88 && box.y + box.height <= height, `scene clipped: ${JSON.stringify(box)}`);
      }
      await page.screenshot({ path: `artifacts/process-${width}x${height}.png` });
    }
    console.log('PASS: process sticky and reversible steps at Full HD and shorter desktop viewports');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
