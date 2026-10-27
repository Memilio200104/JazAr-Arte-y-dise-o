import stripe
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from accounts.views import customer_required
from website.store_presenters import store_context
from shipping.models import ShippingQuote
from shipping.services import fetch_order_rates
from orders.models import Order
from .models import PaymentAttempt, ACTIVE
from .services import start_checkout, reconcile_attempt, apply_session_snapshot
from . import stripe_gateway


@customer_required
@require_http_methods(['GET','POST'])
def checkout(request, public_id):
    order = get_object_or_404(Order, public_id=public_id, customer=request.customer)
    context = dict(order=order, page_title='Envio y pago', rates=[], selected=None)
    status = 200
    attempt = order.payment_attempts.order_by('-created_at').first()
    try:
        if request.method == 'POST':
            action=request.POST.get('action')
            if action == 'quote':
                context['rates']=fetch_order_rates(request.customer,order.pk)
            elif action in ('select','pay'):
                try:
                    quote_id=int(request.POST.get('quote_id',''))
                except (ValueError,TypeError):
                    raise ValidationError('Selecciona una opcion de envio.') from None
                selected=ShippingQuote.objects.filter(pk=quote_id,order=order,customer=request.customer).first()
                if not selected:
                    raise ValidationError('Selecciona una opcion de envio de tu pedido.')
                context['selected']=selected
                if action=='pay':
                    result=start_checkout(request.customer,order.pk,selected.pk)
                    if result.quote:
                        context['selected']=result.quote
                        context['notice']='El envio cambio. Revisa el total actualizado antes de continuar.'
                    else:
                        attempt=result.attempt
                        if attempt.state=='open':
                            return redirect(attempt.checkout_url)
            elif action == 'resume':
                if not attempt or attempt.state not in ACTIVE:
                    raise ValidationError('No hay un pago pendiente para retomar.')
                result=start_checkout(request.customer,order.pk,attempt.quote_id)
                attempt=result.attempt
                if attempt.state=='open':
                    return redirect(attempt.checkout_url)
            elif action == 'refresh':
                if attempt:
                    attempt=reconcile_attempt(attempt.pk,expire=attempt.expires_at <= timezone.now())
            else:
                raise ValidationError('Selecciona una accion valida.')
        # Return is read-only; webhooks/explicit POST refresh reconcile payment state.
        if request.GET.get('retorno') and attempt and attempt.state!='paid':
            context['notice']='Estamos confirmando tu pago. Puedes actualizar su estado en unos instantes.'
    except ValidationError as exc:
        context['error']=' '.join(exc.messages)
    except DatabaseError:
        context['error']='No pudimos actualizar el pedido. Intenta de nuevo en unos instantes.'
        status=503
    attempt=order.payment_attempts.order_by('-created_at').first()
    context['attempt']=attempt
    context['active_payment']=bool(attempt and attempt.state in ACTIVE)
    context['total']=order.subtotal + (context['selected'].amount if context['selected'] else Decimal(0))
    if attempt:
        context['attempt_total']=Decimal(attempt.total_minor)/100
    return render(request,'payments/checkout.html',{**store_context(),**context},status=status)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    if not settings.STRIPE_WEBHOOK_SECRET or not settings.STRIPE_SECRET_KEY.startswith('sk_test_'):
        return HttpResponse(status=503)
    try:
        if len(request.body)>32768:
            return HttpResponse(status=413)
        event=stripe.Webhook.construct_event(request.body,request.headers.get('Stripe-Signature',''),settings.STRIPE_WEBHOOK_SECRET).to_dict()
        if event.get('livemode') is not False:
            return HttpResponse(status=400)
        if event.get('type') not in ('checkout.session.completed','checkout.session.expired','checkout.session.async_payment_succeeded','checkout.session.async_payment_failed'):
            return HttpResponse(status=200)
        data=event['data']['object']
        reference=data.get('client_reference_id')
        attempt=PaymentAttempt.objects.filter(public_id=reference).first() if reference else None
        if not attempt:
            return HttpResponse(status=200)
        session=stripe_gateway.retrieve_session(data['id'])
        apply_session_snapshot(attempt.pk,session,event_id=event['id'])
    except (ValueError,TypeError,KeyError,stripe.SignatureVerificationError):
        return HttpResponse(status=400)
    except (ValidationError,DatabaseError):
        return HttpResponse(status=503)
    return HttpResponse(status=200)
