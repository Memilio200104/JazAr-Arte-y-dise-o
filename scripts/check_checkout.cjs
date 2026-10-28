const {chromium}=require('playwright');
const {spawnSync}=require('node:child_process');
const {randomUUID}=require('node:crypto');
const assert=require('node:assert/strict');
const tag=randomUUID(), password=randomUUID()+'!Aa7';
const setup=spawnSync('.venv/Scripts/python.exe',['manage.py','shell','--settings=config.test_accounts_browser','-c',`
import os,json
from uuid import uuid4
from django.utils import timezone
from datetime import timedelta
from accounts.services import register_customer
from orders.models import Order,OrderItem
from website.models import Product
from shipping.models import ShippingQuote
c=register_customer('Cliente',os.environ['CHECKOUT_TAG']+'@example.com',os.environ['CHECKOUT_PASSWORD'])
p=Product.objects.create(name='Playera personalizada',slug=str(uuid4()),sku=str(uuid4()).upper(),description='Arte',category='prendas',technique_key='dtf',price=250,stock=30,sale_mode='fixed',is_active=True,is_concept=False)
o=Order.objects.create(customer=c,subtotal=500,review_status='approved',idempotency_key=uuid4(),request_digest='a'*64,shipping_address=dict(recipient='Cliente',phone='5512345678',street='Calle',exterior='1',interior='',district='Centro',postcode='55710',city='Coacalco',state='Estado de Mexico',reference=''))
OrderItem.objects.create(order=o,product=p,quantity=2,unit_price=250,sku=p.sku,name=p.name)
q=ShippingQuote.objects.create(order=o,customer=c,fingerprint='a'*64,snapshot={},carrier='DHL',service='Entrega terrestre',amount_minor=18520,expires_at=timezone.now()+timedelta(minutes=10))
print(json.dumps(dict(email=c.email,order=str(o.public_id),quote=q.pk)))
`],{encoding:'utf8',env:{...process.env,CHECKOUT_TAG:tag,CHECKOUT_PASSWORD:password}});
assert.equal(setup.status,0,setup.stderr);
const fixture=JSON.parse(setup.stdout.trim().split(/\r?\n/).at(-1));
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try {
  const context=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'reduce'});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const url='http://127.0.0.1:8011/pedido/'+fixture.order+'/pago/';
  await page.goto(url);await page.getByLabel('Correo electrónico').fill(fixture.email);
  await page.getByLabel('Contraseña',{exact:true}).fill(password);await page.getByRole('button',{name:'Ingresar',exact:true}).click();await page.waitForURL(url);
  // Existing server-rendered quote, no public mock endpoint and no provider calls.
  await page.evaluate(async id=>{
   const body=new URLSearchParams({action:'select',quote_id:String(id),csrfmiddlewaretoken:document.querySelector('[name=csrfmiddlewaretoken]').value});
   const response=await fetch(location.href,{method:'POST',body});document.open();document.write(await response.text());document.close();
  },fixture.quote);
  await page.getByRole('button',{name:'Ir al pago'}).waitFor();
  for(const width of [320,390,844,1440,1920]){
   await page.setViewportSize({width,height:900});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'checkout '+width);
   if([390,1440].includes(width))await page.screenshot({path:'artifacts/checkout-'+width+'.png',fullPage:true});
  }
  await page.getByRole('button',{name:'Ir al pago'}).click();await page.getByRole('alert').waitFor();
  assert.equal(await page.getByText('Pago confirmado',{exact:true}).count(),0);
  const noJS=await browser.newContext({javaScriptEnabled:false,storageState:await context.storageState()});
  const plain=await noJS.newPage();await plain.goto(url);assert.equal(await plain.getByRole('button',{name:'Calcular envio'}).isVisible(),true);
  // Paid fixture belongs only to the isolated browser database; no provider charge.
  const paid=spawnSync('.venv/Scripts/python.exe',['manage.py','shell','--settings=config.test_accounts_browser','-c',`
from payments.models import PaymentAttempt
from shipping.models import ShippingQuote
from django.utils import timezone
q=ShippingQuote.objects.get(pk=${fixture.quote})
PaymentAttempt.objects.create(order=q.order,quote=q,approved_version=q.order.version,total_minor=68520,state='paid',expires_at=timezone.now())
`],{encoding:'utf8'});
  assert.equal(paid.status,0,paid.stderr);
  for(const width of [320,390,844,1440,1920]) {
   await page.setViewportSize({width,height:900});
   for(const path of ['/cuenta/pedidos/','/pedido/'+fixture.order+'/']) {
    await page.goto('http://127.0.0.1:8011'+path);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'paid '+path+' '+width);
    assert.equal(await page.getByText('Pago confirmado',{exact:true}).first().isVisible(),true);
    assert.equal(await page.getByText('$685.20 MXN',{exact:true}).isVisible(),true);
    assert.equal(await page.getByRole('link',{name:'Ver pago',exact:false}).isVisible(),true);
    assert.equal(await page.getByRole('link',{name:'Enviar diseño por WhatsApp',exact:false}).count(),0);
    if([390,1440].includes(width)) await page.screenshot({path:'artifacts/paid-'+(path.includes('cuenta')?'list':'detail')+'-'+width+'.png',fullPage:true});
   }
  }
  await plain.goto('http://127.0.0.1:8011/cuenta/pedidos/');
  assert.equal(await plain.getByRole('link',{name:'Ver pago',exact:false}).isVisible(),true);
  await noJS.close();assert.deepEqual(errors,[]);
  console.log('PASS checkout: private summary, missing credentials error, paid list/detail at five widths, no JS');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
