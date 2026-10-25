import hashlib
import json
import unicodedata
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from orders.models import Order
from .models import ShippingQuote, ShippingRateBucket
from .packing import pack_order
from .envia import quote_rates, ShippingUnavailable


STATES = dict(zip(('aguascalientes,baja california,baja california sur,campeche,chiapas,chihuahua,'
    'ciudad de mexico,coahuila,colima,durango,estado de mexico,guanajuato,guerrero,hidalgo,jalisco,'
    'michoacan,morelos,nayarit,nuevo leon,oaxaca,puebla,queretaro,quintana roo,san luis potosi,'
    'sinaloa,sonora,tabasco,tamaulipas,tlaxcala,veracruz,yucatan,zacatecas').split(','),
    'AG BC BS CM CS CH CX CO CL DG EM GT GR HG JA MI MO NA NL OA PU QT QR SL SI SO TB TM TL VE YU ZA'.split()))


def normalize_address(address):
    name = ''.join(c for c in unicodedata.normalize('NFD', address.get('state', '').lower()) if not unicodedata.combining(c))
    state = STATES.get(name)
    if not state or not str(address.get('postcode', '')).isdigit() or len(address['postcode']) != 5:
        raise ValidationError('Revisa el estado y el codigo postal de la direccion de envio.')
    if address.get('country', 'MX') != 'MX':
        raise ValidationError('El envio solo esta disponible dentro de Mexico.')
    result = dict(name=address.get('recipient', ''), phone=address.get('phone', ''),
        street=address.get('street', ''), number=address.get('exterior', ''),
        district=address.get('district', ''), city=address.get('city', ''), state=state,
        country='MX', postalCode=address['postcode'], reference=address.get('reference', ''))
    if not all(result[k] for k in ('name', 'phone', 'street', 'number', 'city')):
        raise ValidationError('La direccion de envio esta incompleta.')
    if address.get('interior'):
        result['reference'] = ('Interior ' + address['interior'] + '. ' + result['reference'])[:300]
    return result


def order_snapshot(order):
    packed = pack_order(order)
    origin = settings.SHIPPING_ORIGIN
    if not all(origin.get(k) for k in ('name','phone','street','city','state','country','postalCode')):
        raise ShippingUnavailable()
    destination = normalize_address(order.shipping_address)
    prices = {row.product_id: row.unit_price for row in order.items.all()}
    packages = []
    for box in packed.packages:
        packages.append(dict(type='box', content='Articulos personalizados', amount=1,
            declaredValue=float(sum(prices[i['product_id']] * i['quantity'] for i in box['items'])),
            lengthUnit='CM', weightUnit='KG', weight=float(box['weight']),
            dimensions={key: float(box[key]) for key in ('length', 'width', 'height')}))
    snapshot = dict(origin=origin, destination=destination, packages=packages,
        composition=packed.packages, packing_fingerprint=packed.fingerprint,
        carriers=list(settings.ENVIA_CARRIERS), environment='sandbox')
    fingerprint = hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return snapshot, fingerprint


@transaction.atomic
def _consume_limit(customer):
    now = timezone.now()
    bucket, _ = ShippingRateBucket.objects.get_or_create(customer=customer, defaults={'started_at': now})
    ShippingRateBucket.objects.filter(pk=bucket.pk, started_at__lte=now-timedelta(seconds=300)).update(started_at=now, count=0)
    if not ShippingRateBucket.objects.filter(pk=bucket.pk, count__lt=10).update(count=F('count')+1):
        raise ValidationError('Espera unos minutos antes de volver a consultar el envio.')


def fetch_order_rates(customer, order_id, *, fresh=False):
    order = Order.objects.filter(pk=order_id, customer=customer, review_status='approved').first()
    if not order or not customer.user.is_active:
        raise ValidationError('El pedido debe estar aprobado antes de calcular el envio.')
    snapshot, fingerprint = order_snapshot(order)
    now = timezone.now()
    if not fresh:
        cached = list(ShippingQuote.objects.filter(order=order, customer=customer, fingerprint=fingerprint,
            expires_at__gt=now, created_at__gte=now-timedelta(seconds=60)).order_by('amount_minor'))
        if cached:
            return cached
    _consume_limit(customer)
    rates = quote_rates(snapshot['origin'], snapshot['destination'], snapshot['packages'])
    return [ShippingQuote.objects.create(order=order, customer=customer, fingerprint=fingerprint,
        snapshot=snapshot, carrier=rate.carrier, service=rate.service, amount_minor=rate.amount_minor,
        currency=rate.currency, provider_reference=rate.provider_reference,
        expires_at=now+timedelta(seconds=600)) for rate in rates]


def refresh_selected_quote(customer, quote_id):
    old = ShippingQuote.objects.filter(pk=quote_id, customer=customer).first()
    if not old:
        raise ValidationError('Selecciona una opcion de envio de tu pedido.')
    rates = fetch_order_rates(customer, old.order_id, fresh=True)
    fresh = next((r for r in rates if (r.carrier, r.service) == (old.carrier, old.service)), None)
    if fresh is None:
        raise ValidationError('El servicio elegido ya no esta disponible. Consulta otras opciones.')
    changed = (fresh.amount_minor, fresh.currency, fresh.fingerprint) != (old.amount_minor, old.currency, old.fingerprint)
    return fresh, changed
