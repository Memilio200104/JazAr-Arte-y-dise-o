"""Full cancellations with durable intent and canonical Stripe reconciliation."""
from datetime import datetime, timedelta, timezone as dt_timezone

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models import Order
from .models import PaymentAttempt, ProviderEvent, Refund
from . import stripe_gateway as gateway


def capture_payment_details(attempt, session):
    intent = session.get('payment_intent')
    if not isinstance(intent, dict) or intent.get('status') != 'succeeded':
        return
    charge = intent.get('latest_charge')
    if not isinstance(charge, dict):
        return
    valid = (charge.get('livemode') is False and charge.get('paid') is True
             and charge.get('captured') is True and charge.get('status') == 'succeeded'
             and charge.get('currency') == 'mxn'
             and charge.get('amount') == attempt.total_minor
             and charge.get('amount_captured') == attempt.total_minor
             and charge.get('payment_intent') == intent.get('id')
             and str(intent.get('id', '')).startswith('pi_')
             and str(charge.get('id', '')).startswith('ch_')
             and type(charge.get('created')) is int)
    if not valid:
        return
    try:
        paid_at = datetime.fromtimestamp(charge['created'], tz=dt_timezone.utc)
    except (ValueError, OverflowError, OSError):
        return
    if paid_at > timezone.now() or paid_at < attempt.created_at - timedelta(minutes=1):
        return
    if attempt.paid_at:  # Immutable once obtained from canonical Stripe data.
        return
    attempt.paid_at = paid_at
    attempt.charge_id = charge['id']
    attempt.payment_intent_id = intent['id']
    attempt.save(update_fields=['paid_at', 'charge_id', 'payment_intent_id'])


def eligible(attempt):
    return bool(attempt and attempt.state == 'paid' and attempt.currency == 'MXN'
                and 0 < attempt.total_minor < 200000 and attempt.paid_at
                and timedelta(0) <= timezone.now()-attempt.paid_at < timedelta(hours=24))


@transaction.atomic
def _record_request(customer, order_id):
    # Serialize with guide registration on both SQLite and PostgreSQL.
    Order.objects.filter(pk=order_id, customer=customer).update(updated_at=timezone.now())
    attempt = PaymentAttempt.objects.filter(order_id=order_id, order__customer=customer, state='paid').first()
    if not customer.user.is_active or not attempt:
        raise ValidationError('No encontramos un pago confirmado de este pedido.')
    existing = Refund.objects.filter(attempt=attempt).first()
    if existing:
        return existing, False
    if not eligible(attempt) or not attempt.charge_id or not attempt.payment_intent_id:
        raise ValidationError('La cancelación requiere un pago de menos de $2,000 MXN y debe solicitarse antes de cumplir 24 horas desde el pago.')
    return Refund.objects.create(attempt=attempt, amount_minor=attempt.total_minor), True


def request_cancellation(customer, order_id):
    gateway.ensure_configured()
    attempt = PaymentAttempt.objects.filter(order_id=order_id, order__customer=customer, state='paid').first()
    if not attempt or not customer.user.is_active:
        raise ValidationError('No encontramos un pago confirmado de este pedido.')
    if not attempt.paid_at:
        from .services import reconcile_attempt
        reconcile_attempt(attempt.pk)
    refund, created = _record_request(customer, order_id)
    if not created:
        return reconcile_refund(refund.pk)
    return apply_refund_snapshot(refund.pk, gateway.create_refund(refund))


@transaction.atomic
def apply_refund_snapshot(refund_id, snapshot, event_id=None):
    Refund.objects.filter(pk=refund_id).update(updated_at=timezone.now())
    refund = Refund.objects.select_related('attempt').get(pk=refund_id)
    # Refund objects omit livemode; the test-only client and matching canonical
    # charge establish the environment. Reject an explicit live flag as well.
    valid = (isinstance(snapshot, dict) and snapshot.get('livemode') is not True
             and type(snapshot.get('amount')) is int and snapshot['amount'] == refund.amount_minor
             and snapshot.get('currency') == 'mxn'
             and snapshot.get('payment_intent') == refund.attempt.payment_intent_id
             and snapshot.get('charge') == refund.attempt.charge_id
             and (snapshot.get('metadata') or {}).get('cancellation') == str(refund.public_id)
             and isinstance(snapshot.get('id'), str) and snapshot['id'].startswith('re_')
             and (not refund.provider_id or snapshot['id'] == refund.provider_id)
             and snapshot.get('status') in ('pending', 'requires_action', 'succeeded', 'failed', 'canceled'))
    if not valid:
        raise ValidationError('El reembolso necesita revisión administrativa. Conservamos la solicitud.')
    if event_id and ProviderEvent.objects.filter(event_id=event_id).exists():
        return refund
    # A bank may reject a previously succeeded refund days later. Canonical
    # failure takes precedence; stale pending events cannot undo confirmation.
    if refund.state not in ('succeeded', 'failed', 'canceled') or snapshot['status'] == 'failed':
        refund.provider_id = snapshot['id']
        refund.state = 'pending' if snapshot['status'] == 'requires_action' else snapshot['status']
        refund.save(update_fields=['provider_id', 'state', 'updated_at'])
    if event_id:
        ProviderEvent.objects.create(event_id=event_id, attempt=refund.attempt, processed_at=timezone.now())
    return refund


def reconcile_refund(refund_id):
    refund = Refund.objects.select_related('attempt').get(pk=refund_id)
    if refund.provider_id:
        return apply_refund_snapshot(refund.pk, gateway.retrieve_refund(refund.provider_id))
    recovered = gateway.find_refund(refund)
    if recovered:
        return apply_refund_snapshot(refund.pk, recovered)
    # Never reuse an expired idempotency key to issue another refund.
    if refund.requested_at < timezone.now()-timedelta(hours=23):
        raise ValidationError('La cancelación está registrada y necesita revisión administrativa en Stripe.')
    return apply_refund_snapshot(refund.pk, gateway.create_refund(refund))
