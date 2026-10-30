from decimal import Decimal
from django.core import signing
from django.core.exceptions import ValidationError
from website.store_presenters import eligible_products

SALT = 'orders.quote.v1'
ADDRESS_FIELDS = ('recipient','phone','street','exterior','interior','district','postcode','city','state','reference')


def build_quote(customer, rows, address_id, notes):
    if not isinstance(rows,list) or not 1 <= len(rows) <= 100:
        raise ValidationError('Elige entre 1 y 100 productos distintos.')
    if not isinstance(notes,str) or len(notes)>1500:
        raise ValidationError('Las notas deben tener hasta 1500 caracteres.')
    address=customer.addresses.filter(pk=address_id).first()
    if address is None:
        raise ValidationError('Selecciona una dirección de tu cuenta.')
    seen=set(); lines=[]; subtotal=Decimal('0.00')
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'id','quantity','details'}:
            raise ValidationError('Revisa los datos de tu selección.')
        pid,quantity,details=row['id'],row['quantity'],row['details']
        if type(pid) is not int or pid in seen or type(quantity) is not int or not 1<=quantity<=99:
            raise ValidationError('Usa productos distintos y cantidades enteras entre 1 y 99.')
        if not isinstance(details,str) or len(details)>300:
            raise ValidationError('Los detalles de cada pieza admiten hasta 300 caracteres.')
        p=eligible_products().filter(pk=pid).first()
        if p is None or p.currency!='MXN' or p.technique_key=='3d' or p.available_stock is None or p.available_stock<quantity:
            raise ValidationError('Una pieza o cantidad no está disponible. Revisa tu carrito.')
        seen.add(pid)
        lines.append(dict(id=pid,quantity=quantity,details=details.strip(),sku=p.sku,name=p.name,unit_price=str(p.price),stock=p.available_stock))
        subtotal+=p.price*quantity
    if subtotal>Decimal('9999999999.99'):
        raise ValidationError('El importe supera el límite permitido.')
    return dict(owner=customer.pk,rows=lines,address_id=address.pk,
                shipping_address={field:getattr(address,field) for field in ADDRESS_FIELDS},
                notes=notes.strip(),subtotal=str(subtotal),currency='MXN')


def sign_quote(quote):
    return signing.dumps(quote,salt=SALT,compress=True)
