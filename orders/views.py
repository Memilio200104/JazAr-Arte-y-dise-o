import json
from uuid import uuid4
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods, require_GET
from accounts.views import customer_required
from website.store_presenters import store_context
from .forms import RequestForm
from .models import Order
from .quotes import build_quote, sign_quote, SALT
from .services import create_order, QuoteChanged, OrderRateLimited


@customer_required
@require_http_methods(['GET','POST'])
def request_order(request):
    customer=request.customer
    action=request.POST.get('action','')
    form=RequestForm(request.POST if request.method=='POST' and action!='confirm' else None,customer=customer,
                     initial={'address':customer.default_address_id})
    context={'form':form,'page_title':'Demos forma a tu pedido','has_addresses':customer.addresses.exists()}
    status=200
    if request.method=='POST':
        try:
            if action=='confirm':
                token=request.POST.get('quote_token','')
                key=request.POST.get('idempotency_key','')
                # Recover the submitted form for errors without trusting client prices.
                try:
                    prior=signing.loads(token,salt=SALT)
                    if prior.get('owner')==customer.pk:
                        rows=[{k:r[k] for k in ('id','quantity','details')} for r in prior['rows']]
                        form=RequestForm({'rows':json.dumps(rows),'address':prior['address_id'],'notes':prior['notes']},customer=customer)
                        context['form']=form
                        context.update(quote=prior,quote_token=token,idempotency_key=key)
                except (signing.BadSignature,KeyError,TypeError,AttributeError):
                    pass
                order,created=create_order(customer,token,key)
                request.session['submitted_order']={'id':str(order.public_id),'rows':list(order.items.values('product_id','quantity'))}
                return redirect('order_detail',public_id=order.public_id)
            elif action=='preview' and form.is_valid():
                quote=build_quote(customer,form.cleaned_data['rows'],form.cleaned_data['address'].pk,form.cleaned_data['notes'])
                context.update(quote=quote,quote_token=sign_quote(quote),idempotency_key=str(uuid4()))
            elif action not in ('preview','edit'):
                raise ValidationError('Selecciona una acción válida.')
        except OrderRateLimited as exc:
            context['error']='Llegaste al límite de solicitudes. Espera unos minutos antes de volver a enviar.'
            context['retry_after']=exc.retry_after; status=429
        except ValidationError as exc:
            context['error']=' '.join(exc.messages)
            # Require a new preview after changed/expired/invalid quotes.
            context.pop('quote',None)
        except DatabaseError:
            context['error']='No pudimos guardar tu solicitud. Tus datos se conservan; inténtalo de nuevo.'
            status=503
    response=render(request,'orders/request.html',{**store_context(),**context},status=status)
    if status==429: response['Retry-After']=str(context['retry_after'])
    return response


@customer_required
@require_GET
def order_list(request):
    orders=Paginator(request.customer.orders.all(),20).get_page(request.GET.get('page'))
    return render(request,'orders/list.html',{**store_context(),'orders':orders,'page_title':'Tus pedidos'})


@customer_required
@require_GET
def order_detail(request,public_id,payment=False):
    order=get_object_or_404(request.customer.orders.prefetch_related('items'),public_id=public_id)
    submitted=None
    pending=request.session.get('submitted_order')
    if not payment and pending and pending.get('id')==str(order.public_id):
        request.session.pop('submitted_order')
        submitted=[{'id':r['product_id'],'quantity':r['quantity']} for r in pending['rows']]
    return render(request,'orders/detail.html',{**store_context(),'order':order,'payment':payment,
        'submitted_cart':submitted,'page_title':'Tu pedido'})
