"""Customer-facing progress; design approval is never presented as payment."""
from decimal import Decimal

from django.urls import reverse


PAYMENT_COPY = {
    'creating': ('Preparando pago', 'Estamos preparando tu pago. Consulta su estado antes de volver a intentarlo.', 'Consultar pago', 'pending', 'clock'),
    'open': ('Pago pendiente', 'Tu diseño está aprobado. Puedes continuar con el pago de tu pedido.', 'Continuar al pago', 'ready', 'credit-card'),
    'expired': ('Sesión vencida', 'La sesión de pago venció. Consulta el estado y elige de nuevo tu envío para continuar.', 'Revisar envío y pago', 'attention', 'clock'),
    'failed': ('Pago no completado', 'El pago no se completó. Revisa su estado para continuar con tu pedido.', 'Revisar pago', 'attention', 'circle-alert'),
    'reconciliation_required': ('Verificando pago', 'Estamos verificando el resultado del pago. No necesitas iniciar otro.', 'Consultar pago', 'pending', 'clock'),
    'paid': ('Pago confirmado', 'Tu pago quedó registrado. No necesitas volver a pagar ni reenviar tu diseño.', 'Ver pago', 'success', 'circle-check'),
}


def order_progress(order):
    attempts = getattr(order, 'recent_payments', None)
    attempt = (attempts[0] if attempts else None) if attempts is not None else order.latest_payment
    paid = bool(attempt and attempt.state == 'paid')
    if attempt and (paid or order.review_status == 'approved'):
        label, message, action, tone, icon = PAYMENT_COPY.get(attempt.state, PAYMENT_COPY['reconciliation_required'])
        url = reverse('order_payment', args=[order.public_id])
    elif order.review_status == 'approved':
        label, message = 'Diseño aprobado', 'Jazmin aprobó tu diseño. Elige tu envío para continuar al pago.'
        action, tone, icon = 'Elegir envío y pagar', 'ready', 'circle-check'
        url = reverse('order_payment', args=[order.public_id])
    else:
        changes = order.review_status == 'changes'
        label = 'Cambios solicitados' if changes else 'En revisión'
        message = ('Revisa la nota de Jazmin y envía los ajustes de tu diseño por WhatsApp.' if changes
                   else 'Envía tu diseño en PDF o PNG por WhatsApp. Jazmin lo revisará antes del pago.')
        action = 'Enviar ajustes por WhatsApp' if changes else 'Enviar diseño por WhatsApp'
        tone, icon = ('attention', 'pencil-line') if changes else ('pending', 'clock')
        url = f'https://wa.me/525539754777?text=Hola%20Jazmin%2C%20mi%20pedido%20es%20{order.public_id}'
    return dict(label=label, message=message, action_label=action, action_url=url,
                tone=tone, icon=icon, paid=paid, attempt=attempt,
                total=Decimal(attempt.total_minor) / 100 if paid else order.subtotal,
                amount_label='Total pagado' if paid else 'Subtotal de productos')
