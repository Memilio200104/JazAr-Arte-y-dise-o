import hashlib
import json
import math
from datetime import timedelta
from uuid import UUID
from django.core import signing
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone
from .models import Order, OrderItem, OrderCreationBucket, OrderReviewEvent
from .quotes import build_quote, SALT


class QuoteChanged(ValidationError):
    pass


class ReviewConflict(ValidationError):
    pass


@transaction.atomic
def review_order(actor,order_id,expected_version,target_status,note):
    if not actor.is_active or not actor.is_staff or not actor.has_perm('orders.approve_order'):
        raise PermissionDenied
    if target_status not in Order.Status.values or not isinstance(note,str) or len(note)>1500:
        raise ValidationError('Revisa el estado y la nota, de hasta 1500 caracteres.')
    note=note.strip()
    if target_status==Order.Status.CHANGES and not note:
        raise ValidationError('Describe los cambios que necesita el diseño.')
    order=Order.objects.get(pk=order_id)
    if order.version!=expected_version:
        raise ReviewConflict('Otra revisión cambió este pedido. Recarga el pedido antes de guardar.')
    if order.review_status==target_status and order.review_note==note:
        return order
    now=timezone.now()
    approved=target_status==Order.Status.APPROVED
    keep_approval=approved and order.review_status==Order.Status.APPROVED
    changed=Order.objects.filter(pk=order.pk,version=expected_version).update(
        review_status=target_status,review_note=note,version=F('version')+1,updated_at=now,
        approved_by=order.approved_by if keep_approval else (actor if approved else None),
        approved_at=order.approved_at if keep_approval else (now if approved else None))
    if not changed:
        raise ReviewConflict('Otra revisión cambió este pedido. Recarga antes de guardar.')
    OrderReviewEvent.objects.create(order=order,actor=actor,from_status=order.review_status,to_status=target_status,note=note)
    order.refresh_from_db()
    return order


class OrderRateLimited(Exception):
    def __init__(self,retry_after):
        self.retry_after=retry_after


def _existing(customer,key,digest):
    order=Order.objects.filter(customer=customer,idempotency_key=key).first()
    if order and order.request_digest!=digest:
        raise ValidationError('Esta confirmación corresponde a otra selección. Revisa un nuevo resumen.')
    return order


def create_order(customer,quote_token,idempotency_key):
    try:
        key=UUID(str(idempotency_key))
        quote=signing.loads(quote_token,salt=SALT)
    except (ValueError,TypeError,signing.BadSignature):
        raise ValidationError('El resumen no es válido. Solicita uno nuevo.') from None
    if not isinstance(quote,dict) or quote.get('owner')!=customer.pk:
        raise ValidationError('El resumen no pertenece a tu cuenta.')
    digest=hashlib.sha256(json.dumps(quote,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    previous=_existing(customer,key,digest)
    if previous: return previous,False
    try:
        signing.loads(quote_token,salt=SALT,max_age=1800)
    except signing.BadSignature:
        raise ValidationError('El resumen venció. Revisa un nuevo resumen.') from None
    try:
        with transaction.atomic():
            previous=_existing(customer,key,digest)
            if previous: return previous,False
            rows=[{k:r[k] for k in ('id','quantity','details')} for r in quote['rows']]
            try:
                current=build_quote(customer,rows,quote['address_id'],quote['notes'])
            except ValidationError as exc:
                raise QuoteChanged('Cambió la disponibilidad o la dirección. Revisa un nuevo resumen.') from exc
            if current!=quote:
                raise QuoteChanged('Cambió el precio, la disponibilidad o la dirección. Revisa un nuevo resumen.')
            now=timezone.now()
            bucket,_=OrderCreationBucket.objects.get_or_create(customer=customer,defaults={'started_at':now})
            OrderCreationBucket.objects.filter(pk=bucket.pk,started_at__lte=now-timedelta(seconds=900)).update(started_at=now,count=0)
            if not OrderCreationBucket.objects.filter(pk=bucket.pk,count__lt=10).update(count=F('count')+1):
                bucket.refresh_from_db()
                raise OrderRateLimited(max(1,math.ceil(900-(now-bucket.started_at).total_seconds())))
            order=Order.objects.create(customer=customer,subtotal=quote['subtotal'],currency=quote['currency'],
                shipping_address=quote['shipping_address'],notes=quote['notes'],idempotency_key=key,request_digest=digest)
            OrderItem.objects.bulk_create([OrderItem(order=order,product_id=r['id'],sku=r['sku'],name=r['name'],unit_price=r['unit_price'],quantity=r['quantity'],details=r['details']) for r in quote['rows']])
            return order,True
    except IntegrityError:
        previous=_existing(customer,key,digest)
        if previous: return previous,False
        raise
