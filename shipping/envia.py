import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from urllib.request import Request, urlopen
from urllib.error import URLError

from django.conf import settings
from django.core.exceptions import ValidationError


class ShippingUnavailable(ValidationError):
    def __init__(self):
        super().__init__('No pudimos obtener opciones de envio. Intenta de nuevo mas tarde.')


@dataclass(frozen=True)
class Rate:
    carrier: str
    service: str
    amount_minor: int
    currency: str
    provider_reference: str = ''


def parse_rates(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), list):
        raise ShippingUnavailable()
    rates = []
    for row in payload['data']:
        try:
            amount = Decimal(str(row['totalPrice']))
            if (row['currency'] != 'MXN' or not amount.is_finite() or amount <= 0
                    or amount > 999999 or amount * 100 != (amount * 100).to_integral_value()
                    or not isinstance(row['carrier'], str) or not row['carrier']
                    or not isinstance(row['service'], str) or not row['service']):
                continue
            rates.append(Rate(row['carrier'][:80], row['service'][:80], int(amount * 100), 'MXN'))
        except (KeyError, TypeError, InvalidOperation, ValueError):
            continue
    if not rates:
        raise ShippingUnavailable()
    return sorted(rates, key=lambda r: (r.amount_minor, r.carrier, r.service))


def quote_rates(origin, destination, packages):
    if not settings.ENVIA_TOKEN or not 1 <= len(packages) <= 50:
        raise ShippingUnavailable()
    rates = []
    for carrier in settings.ENVIA_CARRIERS[:3]:
        payload = dict(origin=origin, destination=destination, packages=packages,
            shipment={'type': 1, 'carrier': carrier}, settings={'currency': 'MXN'})
        request = Request('https://api-test.envia.com/ship/rate/',
            data=json.dumps(payload).encode(), headers={'Authorization': f'Bearer {settings.ENVIA_TOKEN}',
            'Content-Type': 'application/json',
            'User-Agent': 'JazAr/1.0 (+shipping integration)'}, method='POST')
        try:
            with urlopen(request, timeout=10) as response:
                data = response.read(1024 * 1024 + 1)
                if len(data) > 1024 * 1024:
                    continue
                rates.extend(r for r in parse_rates(json.loads(data)) if r.carrier == carrier)
        except (URLError, TimeoutError, OSError, ValueError, ValidationError):
            continue
    if not rates:
        raise ShippingUnavailable()
    return rates
