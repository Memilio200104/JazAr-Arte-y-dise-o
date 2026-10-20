const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.BASE_URL || 'http://127.0.0.1:8000';
(async () => {
  const browser = await chromium.launch({channel:'chrome',headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:900}});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(base);
    const href = await page.locator('.product[data-sale-mode="fixed"] .product-visual').first().getAttribute('href');
    assert.ok(href.startsWith('/productos/'));
    await page.goto(base + href);
    await page.locator('[data-add-product]').click();
    await page.goto(base + '/carrito/');
    assert.equal(await page.locator('.cart-row').count(),1);
    await page.reload();
    await page.locator('.cart-row input').fill('2');
    await page.locator('.cart-row input').press('Tab');
    assert.equal(await page.locator('.cart-row input').inputValue(),'2');
    const paths = [href,'/carrito/','/cuenta/ingresar/','/cuenta/registro/','/cuenta/recuperar/','/cuenta/','/pedido/solicitud/','/pedido/pago/','/tienda/revision/'];
    for (const width of [320,390,768,844,1024,1440,1920]) {
      await page.setViewportSize({width,height:width === 844 ? 600 : 900});
      for (const path of paths) {
        await page.goto(base+path);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),true,`${path} ${width}`);
        assert.equal(await page.locator('main img').evaluateAll(imgs=>imgs.every(i=>i.complete && i.naturalWidth>0)),true);
        if ([390,1440].includes(width) && ['/carrito/','/cuenta/ingresar/','/pedido/solicitud/','/pedido/pago/'].includes(path)) {
          await page.evaluate(async()=>{await Promise.all(document.getAnimations().map(a=>a.finished.catch(()=>{})));});
          await page.screenshot({path:`artifacts/store-${path.replaceAll('/','-')}-${width}.png`,fullPage:true});
        }
      }
      await page.goto(base+href);
      await page.evaluate(async()=>{await Promise.all(document.getAnimations().map(a=>a.finished.catch(()=>{})));});
      await page.screenshot({path:`artifacts/store-product-${width}.png`,fullPage:true});
      await page.locator('[data-open-photo]').click();
      assert.equal(await page.locator('dialog').evaluate(d=>d.open),true);
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('[data-open-photo]').evaluate(el=>el===document.activeElement),true);
    }
    await page.goto(base+'/carrito/');
    await page.evaluate(()=>{document.body.style.zoom='200%';});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'zoom 200%');
    await page.evaluate(()=>{document.body.style.zoom='';});
    await page.locator('.cart-row button').click();
    assert.equal(await page.locator('[data-cart-empty]').isVisible(),true);
    await page.evaluate(()=>localStorage.setItem('jazar.cart.v1','invalid'));
    await page.reload();
    assert.equal(await page.locator('[data-cart-empty]').isVisible(),true);
    await page.evaluate(()=>localStorage.setItem('jazar.cart.v1',JSON.stringify([{id:-999,quantity:1}])));
    await page.reload();
    assert.equal(await page.locator('.cart-row').count(),0);
    const blocked = await browser.newContext({reducedMotion:'reduce'});
    await blocked.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}});});
    const bp = await blocked.newPage(); await bp.goto(base+href);
    await bp.locator('[data-add-product]').click();
    assert.equal(await bp.locator('[data-cart-count]').textContent(),'1');
    await blocked.close();
    const nojs = await browser.newContext({javaScriptEnabled:false});
    const np = await nojs.newPage(); await np.goto(base+href);
    assert.equal(await np.locator('h1').isVisible(),true);
    await nojs.close();
    assert.deepEqual(errors,[]);
    console.log('Store: routes, selection, 7 widths, dialog, corrupt/blocked storage, no-JS PASS');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
