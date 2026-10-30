# Cancelaciones, reembolsos y seguimiento — Módulo 2

Decisiones comerciales confirmadas el 29 de octubre de 2026:
- Plazo de 24 horas desde el pago confirmado por Stripe, no desde la creación del pedido.
- Total pagado estrictamente menor a $2,000 MXN, incluido el envío. Devolución completa.
- Jazmin genera las guías en Envia y registra transportista, guía y seguimiento desde Django admin. No se compran guías por API.

El cliente confirma expresamente la cancelación desde su pedido. El servidor valida propiedad, pago y plazo; registra una solicitud única antes de llamar a Stripe. El pago original permanece como evidencia contable. La interfaz distingue solicitud, devolución pendiente, confirmación y necesidad de revisión. Los reintentos no duplican devoluciones. Webhooks autenticados y conciliación manual recuperan resultados inciertos. Las claves reales permanecen deshabilitadas.

La fecha de pago procede del cargo exitoso de Stripe. Los pedidos históricos sin esa fecha se concilian antes de evaluar la cancelación. No se usa la fecha de recepción del webhook como inicio del plazo.

No se añade una exclusión comercial por producción/envío que el usuario no aprobó. Las solicitudes deben verse en administración para detener la preparación y gestionar una eventual guía en Envia. No se repone inventario automáticamente: las piezas personalizadas requieren revisión física antes de devolver existencias disponibles.

Seguimiento manual y privado: guía visible solo al dueño del pedido y personal autorizado; enlaces HTTPS, sin compra ni cancelación automática de etiquetas. No se registra un nuevo envío para un pedido con cancelación solicitada. Cambios auditados en administración.

Fuentes técnicas: https://docs.stripe.com/refunds y https://docs.stripe.com/api/refunds/create .
