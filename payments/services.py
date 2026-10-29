from dataclasses import dataclass
from datetime import timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from orders.models import Order
from shipping.models import ShippingQuote
from shipping.services import refresh_selected_quote
from .models import PaymentAttempt, ProviderEvent, ACTIVE
from .inventory import reserve_order, consume_reservation, release_reservation
from . import stripe_gateway as gateway


@dataclass
class CheckoutResult:
    attempt: PaymentAttempt | None = None
    quote: ShippingQuote | None = None


@transaction.atomic
def _prepare_payload(attempt_id):
    attempt = PaymentAttempt.objects.select_related('order','quote').get(pk=attempt_id)
    if attempt.payload:
        return attempt
    origin = settings.PAYMENT_ORIGIN.rstrip('/')
    path = f'/pedido/{attempt.order.public_id}/pago/'
    # Stripe requires at least 30 minutes when it receives the request.
    expires = int(timezone.now().timestamp()) + 1860
    # Endive filters Dashboard-enabled methods through this allowlist.
    payload = dict(mode='payment', allowed_payment_method_types=['card'], locale='es',
        client_reference_id=str(attempt.public_id), expires_at=expires,
        success_url=origin+path+'?retorno=1', cancel_url=origin+path,
        line_items=[{'price_data': {'currency':'mxn', 'unit_amount': int(attempt.order.subtotal*100),
            'product_data': {'name': 'Pedido JazAr ' + str(attempt.order.public_id)}}, 'quantity':1}],
        shipping_options=[{'shipping_rate_data': {'type':'fixed_amount',
            'fixed_amount': {'amount':attempt.quote.amount_minor,'currency':'mxn'},
            'display_name': attempt.quote.carrier.upper() + ' · ' + attempt.quote.service_label}}])
    PaymentAttempt.objects.filter(pk=attempt.pk,payload={}).update(payload=payload)
    attempt.refresh_from_db()
    return attempt


def _recover_creation(attempt):
    if attempt.created_at < timezone.now()-timedelta(hours=23):
        PaymentAttempt.objects.filter(pk=attempt.pk,state='creating').update(state='reconciliation_required')
        raise ValidationError('Este pago necesita revision administrativa antes de continuar.')
    attempt = _prepare_payload(attempt.pk)
    PaymentAttempt.objects.filter(pk=attempt.pk, state='creating').update(creation_requests=F('creation_requests')+1)
    try:
        result = gateway.create_session(attempt)
    except gateway.PaymentRejected:
        with transaction.atomic():
            # A later rejected request cannot disprove an earlier unknown result.
            if PaymentAttempt.objects.filter(pk=attempt.pk,state='creating',session_id__isnull=True,creation_requests=1).update(state='failed'):
                release_reservation(attempt.pk)
        raise
    return apply_session_snapshot(attempt.pk, result)


def start_checkout(customer, order_id, quote_id):
    gateway.ensure_configured()
    order = Order.objects.filter(pk=order_id,customer=customer,review_status='approved').first()
    if not order or not customer.user.is_active:
        raise ValidationError('El pedido debe estar aprobado antes de pagar.')
    existing = order.payment_attempts.filter(state__in=(*ACTIVE,'paid')).first()
    if existing:
        if existing.state == 'creating':
            existing = _recover_creation(existing)
        elif existing.state == 'open' and existing.expires_at <= timezone.now():
            existing = reconcile_attempt(existing.pk, expire=True)
        return CheckoutResult(attempt=existing)
    if not ShippingQuote.objects.filter(pk=quote_id, order=order, customer=customer).exists():
        raise ValidationError('Selecciona una opcion de envio de este pedido.')
    quote, changed = refresh_selected_quote(customer,quote_id)
    if changed:
        return CheckoutResult(quote=quote)
    attempt = reserve_order(order.pk,quote.pk)
    if attempt.state == 'creating':
        attempt = _recover_creation(attempt)
    return CheckoutResult(attempt=attempt)


@transaction.atomic
def apply_session_snapshot(attempt_id, snapshot, event_id=None):
    # A write acquires the SQLite lock before reading mutable payment state.
    PaymentAttempt.objects.filter(pk=attempt_id).update(updated_at=timezone.now())
    attempt = PaymentAttempt.objects.get(pk=attempt_id)
    if event_id and ProviderEvent.objects.filter(event_id=event_id).exists():
        return attempt
    valid = (isinstance(snapshot,dict) and snapshot.get('livemode') is False
        and snapshot.get('client_reference_id') == str(attempt.public_id)
        and snapshot.get('currency') == 'mxn' and type(snapshot.get('amount_total')) is int
        and snapshot['amount_total'] == attempt.total_minor
        and isinstance(snapshot.get('id'),str) and snapshot['id'].startswith('cs_test_')
        and (not attempt.session_id or attempt.session_id == snapshot['id']))
    if not valid:
        if attempt.state != 'paid':
            attempt.state='reconciliation_required'; attempt.save(update_fields=['state','updated_at'])
        return attempt
    state = snapshot.get('status')
    if attempt.state != 'paid':
        paid = state == 'complete' and snapshot.get('payment_status') == 'paid'
        if paid:
            if attempt.reservations.exclude(state='held').exists() or not attempt.reservations.exists():
                attempt.state='reconciliation_required'
            else:
                consume_reservation(attempt.pk)
                attempt.state='paid'
        elif state == 'expired' and attempt.state in ACTIVE:
            release_reservation(attempt.pk)
            attempt.state='expired'
        elif state == 'open' and attempt.state in ('creating','open'):
            url = snapshot.get('url') or ''
            parsed = urlsplit(url)
            if parsed.scheme != 'https' or parsed.hostname != 'checkout.stripe.com' or parsed.username:
                attempt.state='reconciliation_required'
            else:
                attempt.state='open'; attempt.checkout_url=url
        elif state == 'complete':
            attempt.state='reconciliation_required'
        attempt.session_id = snapshot['id']
        attempt.save(update_fields=['state','session_id','checkout_url','updated_at'])
    if event_id:
        ProviderEvent.objects.create(event_id=event_id,attempt=attempt,processed_at=timezone.now())
    return attempt


def reconcile_attempt(attempt_id, *, expire=False):
    attempt = PaymentAttempt.objects.get(pk=attempt_id)
    if attempt.state in ('paid','expired','failed'):
        return attempt
    if not attempt.session_id:
        if attempt.state == 'creating':
            return _recover_creation(attempt)
        raise ValidationError('Este intento requiere revision administrativa.')
    result = gateway.retrieve_session(attempt.session_id)
    if expire and result.get('status') == 'open':
        result = gateway.expire_session(attempt.session_id)
    return apply_session_snapshot(attempt.pk,result)
