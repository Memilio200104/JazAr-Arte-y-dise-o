from urllib.parse import urlsplit
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from orders.models import Order
from payments.models import Refund
from .models import Shipment


@transaction.atomic
def register_shipment(actor, order_id, *, carrier, tracking_number, tracking_url='', status='shipped'):
    if not actor.is_active or not actor.is_staff or not actor.has_perm('shipping.manage_shipment'):
        raise PermissionDenied
    Order.objects.filter(pk=order_id).update(updated_at=timezone.now())
    order = Order.objects.get(pk=order_id)
    if not order.payment_attempts.filter(state='paid').exists():
        raise ValidationError('Primero debe confirmarse el pago del pedido.')
    if Refund.objects.filter(attempt__order=order).exists():
        raise ValidationError('Este pedido tiene una cancelación solicitada. Revisa su devolución y gestiona la guía en Envia.')
    shipment = Shipment.objects.filter(order=order).first() or Shipment(order=order)
    shipment.carrier = carrier.strip()
    shipment.tracking_number = tracking_number.strip()
    shipment.tracking_url = tracking_url.strip()
    shipment.status = status
    shipment.updated_by = actor
    if shipment.tracking_url:
        try:
            url = urlsplit(shipment.tracking_url)
            valid = url.scheme == 'https' and url.hostname and not url.username and not url.password
        except ValueError:
            valid = False
        if not valid:
            raise ValidationError('Usa un enlace HTTPS de seguimiento del transportista.')
    shipment.full_clean()
    shipment.save()
    return shipment
