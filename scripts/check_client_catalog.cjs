const { chromium } = require('playwright');
const assert = require('node:assert/strict');
let browser;
(async () => {
  browser = await chromium.launch({channel:'chrome',headless:true});
  const page = await browser.newPage({viewport:{width:1536,height:960},reducedMotion:'reduce'});
  await page.goto('http://127.0.0.1:8000/',{waitUntil:'networkidle'});
  assert.equal(await page.locator('.product[data-sale-mode="fixed"]').count(),79);
  assert.equal(await page.locator('.product[data-sale-mode="quote"]').count(),6);
  assert.equal(await page.locator('a[href="https://wa.me/525539754777"]').count(),1);
  for (const width of [1536,390]) {
    await page.setViewportSize({width,height:960});
    for (const [name,selector] of [['owner','.intro'],['catalog','#catalogo'],['social','.contact-socials']]) {
      await page.locator(selector).scrollIntoViewIfNeeded();
      for (const img of await page.locator(`${selector} img`).all()) {
        await img.scrollIntoViewIfNeeded();
        await img.evaluate(i=>i.decode());
      }
      await page.locator(selector).evaluate(el=>el.scrollIntoView({block:'start',behavior:'instant'}));
      await page.screenshot({path:`artifacts/client-${name}-${width}.png`});
    }
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    const social=page.locator('.contact-socials');
    assert.ok(await social.locator('img').evaluateAll(images=>images.every(i=>i.naturalWidth>0)));
    assert.ok(await social.locator('a').evaluateAll(links=>links.every(a=>a.getBoundingClientRect().height>=44)));
  }
  console.log('PASS: 79 fixed-price products, 6 quoted products, social links, images and desktop/mobile layout.');
  await browser.close();
})().catch(async e=>{console.error(e);await browser?.close();process.exitCode=1;});
