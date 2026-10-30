import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from .models import ProductPacking


@dataclass(frozen=True)
class PackingResult:
    packages: list[dict]
    fingerprint: str


def pack_order(order):
    rows = list(order.items.all())
    if not rows or len(rows) > 100:
        raise ValidationError('El pedido no tiene una seleccion valida para envio.')
    mappings = {p.product_id: p for p in ProductPacking.objects.select_related('profile').filter(
        product_id__in=[r.product_id for r in rows])}
    units, configuration = [], []
    for row in sorted(rows, key=lambda r: r.product_id):
        packing = mappings.get(row.product_id)
        if not packing or not packing.profile.active:
            raise ValidationError('Falta configurar el empaque de uno de los productos. Contactanos para revisarlo.')
        box = packing.profile
        weight = packing.protected_unit_weight_kg
        capacity = packing.capacity_units
        if (row.quantity < 1 or row.quantity > 99 or capacity < 1 or capacity > box.capacity
                or weight <= 0 or box.tare_kg <= 0 or box.tare_kg + weight > box.max_weight_kg
                or min(box.length_cm, box.width_cm, box.height_cm) <= 0):
            raise ValidationError('Las medidas o el peso del empaque necesitan revision.')
        configuration.append([row.product_id, row.quantity, box.pk, str(weight), capacity,
            str(box.length_cm), str(box.width_cm), str(box.height_cm), str(box.tare_kg),
            str(box.max_weight_kg), box.capacity])
        units.extend((packing, row.product_id) for _ in range(row.quantity))
    units.sort(key=lambda unit: (-unit[0].capacity_units, -unit[0].protected_unit_weight_kg, unit[1]))
    boxes = []
    for packing, product_id in units:
        profile = packing.profile
        target = next((b for b in boxes if b['profile_id'] == profile.pk
            and b['_capacity'] + packing.capacity_units <= profile.capacity
            and b['_weight'] + packing.protected_unit_weight_kg <= profile.max_weight_kg), None)
        if target is None:
            target = {'profile_id': profile.pk, 'length': str(profile.length_cm),
                'width': str(profile.width_cm), 'height': str(profile.height_cm),
                '_weight': profile.tare_kg, '_capacity': 0, '_items': {}}
            boxes.append(target)
        target['_weight'] += packing.protected_unit_weight_kg
        target['_capacity'] += packing.capacity_units
        target['_items'][product_id] = target['_items'].get(product_id, 0) + 1
    for box in boxes:
        box['weight'] = str(box.pop('_weight').quantize(Decimal('.001')))
        box.pop('_capacity')
        box['items'] = [{'product_id': key, 'quantity': value} for key, value in sorted(box.pop('_items').items())]
    fingerprint = hashlib.sha256(json.dumps(configuration, separators=(',', ':')).encode()).hexdigest()
    return PackingResult(boxes, fingerprint)
