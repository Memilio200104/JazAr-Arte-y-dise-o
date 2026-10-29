const {chromium}=require('playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try {
  const page=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
  const errors=[]; page.on('pageerror',e=>errors.push(e.message));
  let releaseImage;
  const imageGate=new Promise(resolve=>releaseImage=resolve);
  await page.route('**/images/brand/jazar-original.png',async route=>{await imageGate;await route.continue();});
  await page.goto('http://127.0.0.1:8000/cuenta/ingresar/',{waitUntil:'domcontentloaded'});
  await page.locator('[data-page-loading]:not([hidden])').waitFor();
  assert.equal(await page.locator('.loading-spinner').evaluate(el=>getComputedStyle(el).animationName),'none');
  await page.screenshot({path:'artifacts/loading-initial-390.png'});
  releaseImage(); await page.waitForLoadState('load');
  await page.locator('[data-page-loading]').waitFor({state:'hidden'});
  await page.getByRole('button',{name:'Ingresar',exact:true}).click();
  assert.equal(await page.locator('[data-page-loading]').isVisible(),false,'invalid form must not start loading');
  // Focused checkout fixture exercises native submission without provider traffic.
  const html=`<html><head><style>${fs.readFileSync('static/css/loading.css','utf8')}</style></head><body>
  <div data-page-loading class="page-loading" hidden><span class="loading-spinner"></span><span data-loading-message role="status"></span></div>
  <a href="#same">Dentro de la página</a><a href="/delayed-page">Otra página</a>
  <div data-checkout><p data-payment-feedback role="status"></p><form method="post" action="/delayed-payment">
  <button name="action" value="quote">Calcular envío</button><button disabled>Bloqueado</button></form></div></body></html>`;
  await page.setContent(html);
  await page.addScriptTag({content:fs.readFileSync('static/js/loading.js','utf8')});
  await page.addScriptTag({content:fs.readFileSync('static/js/checkout.js','utf8')});
  // Dispatch the native submit event without navigating; check_checkout covers real POSTs.
  const submitted=await page.evaluate(()=>{
   const form=document.querySelector('[data-checkout] form'), button=form.querySelector('[name=action]');
   form.dispatchEvent(new SubmitEvent('submit',{bubbles:true,cancelable:true,submitter:button}));
   return new URLSearchParams(new FormData(form)).toString();
  });
  await page.waitForFunction(()=>document.querySelector('[data-submitting]')?.textContent==='Calculando envío…',null,{timeout:3000});
  assert.equal(await page.evaluate(()=>document.querySelector('[data-submitting]').disabled),true);
  await page.waitForFunction(()=>!document.querySelector('[data-page-loading]').hidden,null,{timeout:3000});
  assert.match(submitted,/action=quote/,'disabling button must preserve submitted action');
  assert.equal(await page.evaluate(()=>document.querySelector('[data-checkout] form').getAttribute('aria-busy')),'true');
  await page.screenshot({path:'artifacts/loading-checkout-390.png'});
  await page.evaluate(()=>window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true})));
  assert.equal(await page.evaluate(()=>document.querySelector('button[name=action]').disabled),false);
  assert.equal(await page.evaluate(()=>document.querySelector('button:not([name])').disabled),true);
  assert.equal(await page.evaluate(()=>document.querySelectorAll('[data-submit-action]').length),0);
  await page.setContent(html); await page.addScriptTag({content:fs.readFileSync('static/js/loading.js','utf8')});
  await page.getByRole('link',{name:'Dentro de la página'}).click();
  assert.equal(await page.locator('[data-page-loading]').isVisible(),false);
  await page.route('**/delayed-page',async route=>{await new Promise(resolve=>setTimeout(resolve,600));await route.fulfill({body:'<p>Listo</p>',contentType:'text/html'});});
  await page.getByRole('link',{name:'Otra página'}).click();
  await page.waitForURL('**/delayed-page');
  const plain=await browser.newPage({javaScriptEnabled:false});
  await plain.goto('http://127.0.0.1:8000/cuenta/ingresar/');
  assert.equal(await plain.locator('[data-page-loading]').isVisible(),false);
  assert.deepEqual(errors,[]);
  console.log('PASS loading: slow initial image/navigation/checkout, action preserved, invalid form, reduced motion, pageshow reset, no JS');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1)});
