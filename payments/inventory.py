from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from orders.models import Order
from website.models import Product
from shipping.models import ShippingQuote
from shipping.services import order_snapshot
from .models import PaymentAttempt, StockReservation, ACTIVE


@transaction.atomic
def reserve_order(order_id, quote_id):
    # Acquire the order write lock before reading: SQLite cannot upgrade two
    # concurrent shared read locks reliably. Review edits use this same version.
    if not Order.objects.filter(pk=order_id).update(version=F('version')+1):
        raise ValidationError('El pedido ya no esta disponible.')
    order = Order.objects.get(pk=order_id)
    if order.review_status != 'approved' or not order.customer.user.is_active:
        raise ValidationError('El pedido necesita aprobacion antes de pagar.')
    existing = order.payment_attempts.filter(state__in=(*ACTIVE,'paid')).first()
    if existing:
        return existing
    quote = ShippingQuote.objects.filter(pk=quote_id, order=order, customer=order.customer, expires_at__gt=timezone.now()).first()
    if not quote or quote.currency != 'MXN' or quote.fingerprint != order_snapshot(order)[1]:
        raise ValidationError('El envio cambio o vencio. Consulta nuevamente.')
    items = list(order.items.select_related('product').order_by('product_id'))
    subtotal = sum(int(row.unit_price*100)*row.quantity for row in items)
    if not items or order.currency != 'MXN' or subtotal != int(order.subtotal*100):
        raise ValidationError('El importe del pedido necesita revision.')
    attempt = PaymentAttempt.objects.create(order=order, quote=quote, approved_version=order.version,
        total_minor=subtotal+quote.amount_minor, expires_at=timezone.now()+timedelta(minutes=30))
    for row in items:
        changed = Product.objects.filter(pk=row.product_id, is_active=True, is_concept=False,
            sale_mode='fixed', currency='MXN', stock__gte=F('reserved_stock')+row.quantity).exclude(technique_key='3d').update(
                reserved_stock=F('reserved_stock')+row.quantity)
        if not changed:
            raise ValidationError('Ya no hay suficientes existencias. Revisa tu pedido.')
        StockReservation.objects.create(attempt=attempt, product_id=row.product_id, quantity=row.quantity)
    return attempt


@transaction.atomic
def consume_reservation(attempt_id):
    for reservation in StockReservation.objects.filter(attempt_id=attempt_id, state='held').order_by('product_id'):
        if StockReservation.objects.filter(pk=reservation.pk,state='held').update(state='consumed'):
            if not Product.objects.filter(pk=reservation.product_id,stock__gte=reservation.quantity,
                    reserved_stock__gte=reservation.quantity).update(stock=F('stock')-reservation.quantity,
                    reserved_stock=F('reserved_stock')-reservation.quantity):
                raise ValidationError('Las existencias requieren conciliacion.')


@transaction.atomic
def release_reservation(attempt_id):
    for reservation in StockReservation.objects.filter(attempt_id=attempt_id,state='held').order_by('product_id'):
        if StockReservation.objects.filter(pk=reservation.pk,state='held').update(state='released'):
            if not Product.objects.filter(pk=reservation.product_id,reserved_stock__gte=reservation.quantity).update(
                    reserved_stock=F('reserved_stock')-reservation.quantity):
                raise ValidationError('La reserva requiere conciliacion.')
