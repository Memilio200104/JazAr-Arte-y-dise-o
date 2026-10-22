const {chromium}=require('playwright');
const {spawnSync}=require('node:child_process');
const {randomUUID}=require('node:crypto');
const assert=require('node:assert/strict');
const id=randomUUID(), password=randomUUID()+'!Aa7';
const seed=spawnSync('.venv/Scripts/python.exe',['manage.py','shell','--settings=config.test_accounts_browser','-c',`
import os,json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from accounts.services import register_customer,save_address
from website.models import Product
tag=os.environ['ORDER_TEST_ID']; password=os.environ['ORDER_TEST_PASSWORD']
customer=register_customer('Cliente de prueba',tag+'@example.com',password)
save_address(customer,dict(label='Casa',recipient='Persona',phone='5512345678',street='Calle de prueba',exterior='1',interior='',district='Centro',postcode='01234',city='Ciudad',state='Estado',reference=''))
staff=get_user_model().objects.create_user('staff-'+tag,password=password,is_staff=True)
staff.user_permissions.add(*Permission.objects.filter(content_type__app_label='orders',codename__in=['view_order','approve_order','view_orderitem','view_orderreviewevent']))
p=Product.objects.create(name='Taza de prueba',slug=tag,sku=tag.upper(),description='Arte',category='regalos',technique_key='sublimacion',price='199.90',sale_mode='fixed',stock=30,is_active=True,is_concept=False)
print(json.dumps({'product':p.pk,'email':customer.email,'staff':staff.username}))
`],{encoding:'utf8',env:{...process.env,ORDER_TEST_ID:id,ORDER_TEST_PASSWORD:password}});
if(seed.status!==0) throw new Error('Isolated fixture setup failed: '+seed.stderr);
const fixture=JSON.parse(seed.stdout.trim().split(/\r?\n/).at(-1));
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try {
  const root='http://127.0.0.1:8011', page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(root+'/cuenta/ingresar/?next=/pedido/solicitud/');
  await page.evaluate(pid=>localStorage.setItem('jazar.cart.v1',JSON.stringify([{id:pid,quantity:2}])),fixture.product);
  await page.getByLabel('Correo electrónico').fill(fixture.email);await page.getByLabel('Contraseña',{exact:true}).fill(password);
  await page.getByRole('button',{name:'Ingresar',exact:true}).click();await page.waitForURL(root+'/pedido/solicitud/');
  await page.getByLabel('Talla, color y detalles (opcional)').fill('Azul');
  await page.getByLabel('Notas para Jazmin (opcional)').fill('Diseño por WhatsApp');
  for(const width of [320,390,844,1440,1920]) {
   await page.setViewportSize({width,height:900});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'request '+width);
   if([390,1440].includes(width)) await page.screenshot({path:'artifacts/order-request-'+width+'.png',fullPage:true});
  }
  await page.getByRole('button',{name:'Revisar resumen'}).click();
  await page.getByRole('button',{name:'Solicitar revisión'}).waitFor();
  const beforeFailure=await page.evaluate(()=>localStorage.getItem('jazar.cart.v1'));
  const setStock=n=>{
   const result=spawnSync('.venv/Scripts/python.exe',['manage.py','shell','--settings=config.test_accounts_browser','-c',`from website.models import Product; Product.objects.filter(pk=${fixture.product}).update(stock=${n})`],{encoding:'utf8'});
   assert.equal(result.status,0);
  };
  setStock(1);
  await page.getByRole('button',{name:'Solicitar revisión'}).click();
  await page.locator('[data-order-error]').waitFor();
  assert.equal(await page.evaluate(()=>localStorage.getItem('jazar.cart.v1')),beforeFailure,'Failed confirmation preserves raw cart');
  setStock(30);
  await page.getByRole('button',{name:'Revisar resumen'}).click();
  await page.getByRole('button',{name:'Solicitar revisión'}).waitFor();
  await page.getByRole('button',{name:'Solicitar revisión'}).click();await page.waitForURL(/\/pedido\/[a-f0-9-]+\/$/);
  const detail=page.url();
  assert.deepEqual(await page.evaluate(()=>JSON.parse(localStorage.getItem('jazar.cart.v1') || '[]')),[]);
  assert.equal(await page.getByRole('button',{name:'Pago no disponible'}).isDisabled(),true);
  const admin=await browser.newPage({viewport:{width:1440,height:900}});
  await admin.goto(root+'/admin/login/');await admin.locator('#id_username').fill(fixture.staff);await admin.locator('#id_password').fill(password);await admin.locator('input[type=submit]').click();
  await admin.goto(root+'/admin/orders/order/');
  await admin.getByRole('link',{name:detail.split('/').at(-2),exact:true}).click();
  await admin.getByLabel('Diseño revisado y aprobado por Jazmin').check();
  await admin.getByRole('button',{name:'Guardar revisión'}).click();
  await page.reload();await page.getByRole('heading',{name:'Tu diseño está aprobado.'}).waitFor();
  assert.equal(await page.getByRole('button',{name:'Pago no disponible'}).isDisabled(),true);
  for(const width of [320,390,844,1440,1920]) {
   await page.setViewportSize({width,height:900});
   for(const path of [detail,root+'/cuenta/pedidos/',root+'/pedido/solicitud/']) {
    await page.goto(path); assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,path+' '+width);
   }
   if([390,1440].includes(width)) {await page.goto(detail);await page.screenshot({path:'artifacts/orders-'+width+'.png',fullPage:true});}
  }
  await admin.setViewportSize({width:390,height:844});
  assert.equal(await admin.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'admin mobile');
  await admin.screenshot({path:'artifacts/order-admin-390.png',fullPage:true});
  await admin.getByLabel('Diseño revisado y aprobado por Jazmin').uncheck();await admin.getByLabel('Solicitar cambios al cliente').check();await admin.getByLabel('Nota visible para el cliente').fill('Envía PNG con fondo transparente.');await admin.getByRole('button',{name:'Guardar revisión'}).click();
  await page.goto(detail);await page.getByText('Envía PNG con fondo transparente.',{exact:true}).waitFor();
  // A newer selection in another tab must survive a successful submission.
  await page.evaluate(pid=>localStorage.setItem('jazar.cart.v1',JSON.stringify([{id:pid,quantity:1}])),fixture.product);
  await page.goto(root+'/pedido/solicitud/');await page.getByRole('button',{name:'Revisar resumen'}).click();await page.getByRole('button',{name:'Solicitar revisión'}).waitFor();
  await page.evaluate(pid=>localStorage.setItem('jazar.cart.v1',JSON.stringify([{id:pid,quantity:3}])),fixture.product);
  await page.getByRole('button',{name:'Solicitar revisión'}).click();await page.waitForURL(/\/pedido\/[a-f0-9-]+\/$/);
  assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('jazar.cart.v1'))[0].quantity),3);
  const noJS=await browser.newContext({javaScriptEnabled:false,storageState:await page.context().storageState()});
  const noJSPage=await noJS.newPage();await noJSPage.goto(detail);
  assert.equal(await noJSPage.getByRole('heading',{name:'Un ajuste para seguir.'}).isVisible(),true);
  await noJSPage.goto(root+'/pedido/solicitud/');
  assert.equal(await noJSPage.locator('main noscript p').isVisible(),true);
  await noJS.close();
  assert.deepEqual(errors,[]);
  console.log('PASS orders: request, snapshot, staff approval/revocation, disabled payment, 5 widths, concurrent cart preservation');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
