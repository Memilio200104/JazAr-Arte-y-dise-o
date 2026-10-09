const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle' });
    const travel = await page.evaluate(() => {
      const trigger = ScrollTrigger.getById('hero-story');
      return trigger ? trigger.end - trigger.start : 0;
    });
    assert.ok(travel >= 600, `Hero has no scroll sequence: ${travel}px`);
    const first = await page.locator('.hero').boundingBox();
    await page.evaluate(() => scrollTo({ top: 400, behavior: 'instant' }));
    await page.waitForFunction(() => ScrollTrigger.getById('hero-story').progress > .2);
    const during = await page.locator('.hero').boundingBox();
    assert.ok(Math.abs(first.y - during.y) < 3, 'Hero must remain pinned');
    await page.screenshot({ path: 'artifacts/hero-1920-scroll.png' });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.waitForFunction(() => !ScrollTrigger.getById('hero-story'));
    assert.equal(await page.evaluate(() => !!ScrollTrigger.getById('hero-story')), false);
    assert.equal(await page.locator('.pin-spacer').count(), 0);
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForFunction(() => !document.querySelector('.pin-spacer'));
    assert.equal(await page.locator('.pin-spacer').count(), 0);
    console.log('PASS: 1920x1080 hero scroll travel, pin, reduced motion and mobile cleanup');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
