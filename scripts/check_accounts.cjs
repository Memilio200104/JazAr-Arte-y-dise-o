const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {randomUUID}=require('node:crypto');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const root='http://127.0.0.1:8011', email=`test-${randomUUID()}@example.com`, password=randomUUID()+'!Aa7';
  await page.goto(root+'/cuenta/registro/');
  await page.getByLabel('Nombre completo',{exact:true}).fill('Persona de prueba');
  await page.getByLabel('Correo electrónico',{exact:true}).fill(email);
  await page.getByLabel('Contraseña',{exact:true}).fill(password);
  await page.getByLabel('Confirma tu contraseña').fill(password);
  await page.getByRole('button',{name:'Crear cuenta'}).click();
  await page.waitForURL(root+'/cuenta/');
  assert.equal(await page.getByText('Pendiente de verificación',{exact:true}).count(),1);
  await page.getByLabel('Nombre completo').fill('Nombre actualizado');
  await page.getByRole('button',{name:'Guardar nombre'}).click();
  await page.waitForURL(root+'/cuenta/');
  for (const label of ['Casa','Trabajo']) {
   await page.goto(root+'/cuenta/direcciones/nueva/');
   for (const [field,value] of Object.entries({label,recipient:'Persona receptora',phone:'55 1234 5678',street:'Calle de prueba',exterior:'10',district:'Centro',postcode:'01234',city:'Municipio',state:'Ciudad de México'})) await page.locator(`#id_${field}`).fill(value);
   await page.getByRole('button',{name:'Guardar dirección'}).click();
   await page.waitForURL(root+'/cuenta/direcciones/');
  }
  await page.locator('.address-list article').filter({has:page.getByRole('heading',{name:'Trabajo'})}).getByRole('button',{name:'Usar como predeterminada'}).click();
  assert.equal(await page.locator('.address-list article').filter({hasText:'Trabajo'}).getByText('Predeterminada',{exact:true}).count(),1);
  for (const width of [320,390,844,1440,1920]) {
   await page.setViewportSize({width,height:width===844?600:900});
   for(const path of ['/cuenta/','/cuenta/direcciones/','/cuenta/direcciones/nueva/']) {
    await page.goto(root+path);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,path+' '+width);
    if(path==='/cuenta/') {
     const orders=page.getByRole('link',{name:'Mis pedidos',exact:true});
     assert.equal(await orders.isVisible(),true);
     assert.equal(await orders.getAttribute('href'),'/cuenta/pedidos/');
     assert.ok((await orders.boundingBox()).height>=44);
     if([390,1440].includes(width)) await page.screenshot({path:`artifacts/account-orders-${width}.png`,fullPage:true});
    }
    assert.equal(await page.locator('.account-links').evaluate(el=>getComputedStyle(el).position),'static','Account navigation must stay in its section');
   }
   if([390,1440].includes(width)) await page.screenshot({path:`artifacts/accounts-address-${width}.png`,fullPage:true});
  }
  await page.goto(root+'/cuenta/direcciones/');
  await page.locator('.address-list article').filter({hasText:'Trabajo'}).getByRole('link',{name:'Eliminar',exact:true}).click();
  await page.getByRole('button',{name:'Eliminar dirección',exact:true}).click();
  await page.waitForURL(root+'/cuenta/direcciones/');
  assert.equal(await page.locator('.address-list article').count(),1);
  await page.getByRole('button',{name:'Cerrar sesión'}).click();
  await page.goto(root+'/cuenta/ingresar/');
  await page.getByLabel('Correo electrónico').fill(email);
  await page.getByLabel('Contraseña',{exact:true}).fill(password);
  await page.getByRole('button',{name:'Ingresar',exact:true}).click();
  await page.waitForURL(root+'/cuenta/');
  assert.equal(await page.getByLabel('Nombre completo').inputValue(),'Nombre actualizado');
  await page.getByRole('button',{name:'Cerrar sesión'}).click();
  await page.goto(root+'/cuenta/recuperar/');
  await page.locator('input[type=email]').fill(email);
  await page.getByRole('button',{name:'Solicitar enlace'}).click();
  await page.waitForURL(root+'/cuenta/recuperar/listo/');
  assert.deepEqual(errors,[]);
  console.log('PASS accounts: register/login/name/address defaults/delete/logout/recovery, 5 widths; isolated test database');
 } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1)});
