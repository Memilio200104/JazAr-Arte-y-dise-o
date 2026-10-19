const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage();
    for (const [width, height] of [[844, 836], [768, 700], [1023, 650], [1920, 1080], [1536, 728], [1280, 650]]) {
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
    // Resize the same page across the breakpoint to catch stale GSAP styles.
    for (const [width,height] of [[390,844],[767,800],[844,836],[844,599],[768,600],[320,568]]) {
      await page.setViewportSize({width,height});
      const animated = width >= 768 && height >= 600;
      await page.waitForFunction(expected => (getComputedStyle(document.querySelector('.process-scene')).display !== 'none') === expected, animated);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`overflow ${width}x${height}`);
      if (!animated) {
        const image=page.locator('#paso-1 .scene-mobile-image');
        assert.ok((await image.boundingBox()).height<=Math.min(320,height*.42)+1);
        await page.locator('#paso-1').scrollIntoViewIfNeeded();
      } else {
        await page.locator('[data-goto-step="2"]').click();
        await page.waitForFunction(()=>document.querySelector('#process-number').textContent==='02');
      }
      await page.screenshot({path:`artifacts/process-resize-${width}x${height}.png`});
    }
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.setViewportSize({width:844,height:836});
    assert.equal(await page.locator('.process-scene').isVisible(),false);
    console.log('PASS: sticky/reversible process, Codex-sized panels, breakpoint resizing, short/mobile fallback and reduced motion');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
