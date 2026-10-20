const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
  const browser=await chromium.launch({channel:'chrome',headless:true});
  try {
    const page=await browser.newPage();
    for(const status of [400,403,404,500]) {
      const url=`http://127.0.0.1:8000/tienda/revision/errores/${status}/`;
      for(const width of [320,390,844,1440]) {
        await page.setViewportSize({width,height:900});
        const response=await page.goto(url,{waitUntil:'networkidle'});
        assert.equal(response.status(),status);
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
        await page.locator('.artwork img').evaluate(i=>i.decode());
        assert.equal(await page.getByRole('link',{name:'Volver al inicio'}).getAttribute('href'),'/');
        await page.screenshot({path:`artifacts/error-${status}-${width}.png`,fullPage:true});
      }
    }
    assert.equal((await page.request.get('http://127.0.0.1:8000/static/icons/favicon.ico')).status(),200);
    console.log('PASS: 400/403/404/500 previews at four widths, real assets, recovery links and favicon. HTTP handler integration covered in Django tests.');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
