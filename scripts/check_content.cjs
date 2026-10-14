const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    for (const width of [320, 390, 768, 1536, 1920]) {
      const page = await browser.newPage({ viewport: { width, height: 864 }, reducedMotion: 'reduce' });
      await page.goto('http://127.0.0.1:8000/');
      await page.evaluate(() => {
        document.querySelector('.hero h2').textContent = 'Una idea personalizada para transformar cada momento en una pieza especial hecha para ti y tu equipo';
        document.querySelector('.hero-description').textContent = 'Creamos prendas y regalos personalizados para celebrar los momentos especiales de tu familia y de tu equipo. '.repeat(5);
      });
      const hero = await page.locator('.hero').boundingBox();
      const button = await page.locator('.hero .button').boundingBox();
      assert.ok(button.y + button.height < hero.y + hero.height, `CTA clipped at ${width}`);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      await page.close();
    }
    console.log('PASS: long editable hero at five widths');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
