# Cancelaciones y seguimiento — cierre funcional del Módulo 2 en pruebas

Implementación del 29 de octubre; cierre documental el 30 de octubre de 2026. Se conserva el modo de pruebas de Stripe y Envia. No hay despliegue ni cobros reales habilitados.

## Política confirmada

- Cancelación solicitada antes de cumplir 24 horas desde el pago confirmado.
- Total pagado estrictamente menor a $2,000 MXN, incluido el envío. $2,000 exactos no aplica.
- Devolución completa al mismo medio de pago. El sitio no promete una fecha de abono bancario.
- No se añadió exclusión por producción o envío. Jazmin debe revisar las cancelaciones para detener preparación y resolver cualquier guía ya comprada directamente en Envia.
- No se repone inventario automáticamente: se revisa físicamente la posibilidad de reutilizar las piezas antes de ajustar existencias.

## Cliente

En **Mis pedidos → Ver pedido**, un pago elegible muestra **Solicitar cancelación**. La pantalla explica importe y plazo y exige marcar una confirmación antes del POST. GET no cancela ni devuelve dinero. Las 24 horas se verifican nuevamente en el servidor. Para pagos históricos sin fecha, el POST concilia primero el cargo canónico de Stripe; no reinicia el plazo con la fecha de recepción local.

Una solicitud persistida bloquea nuevos envíos. Distingue cancelación solicitada, devolución en proceso, confirmación y revisión por fallo. Conserva el pago original y su importe. El cliente puede consultar la devolución pendiente sin generar solicitudes nuevas. Si Stripe informa después que el banco rechazó una devolución inicialmente confirmada, el sitio cambia a revisión administrativa.

El seguimiento se muestra solo al dueño del pedido: transportista, guía, estado manual En camino/Entregado y enlace HTTPS opcional. No implica sincronización automática con la paquetería.

## Jazmin / administración

1. Generar la guía en Envia, fuera de JazAr.
2. Abrir **Admin → Orders → pedido pagado**. En **Guía y seguimiento**, registrar transportista, número y enlace público HTTPS; indicar En camino al entregar el paquete al transportista.
3. Actualizar a Entregado cuando se confirme la entrega. Las modificaciones quedan en el historial administrativo.
4. Revisar **Payments → Cancelaciones y reembolsos**, y los avisos de cancelación dentro de cada pedido. La acción **Consultar / recuperar devolución en Stripe** concilia el resultado; no permite editar importes ni marcar manualmente una devolución exitosa.

Permisos específicos, además de staff activo: `orders.view_order` + `shipping.manage_shipment` para guías; `payments.view_refund` + `payments.reconcile_refund` para conciliación. Un superusuario ya los incluye. No se conceden estos permisos a compradores.

No crear un reembolso nuevo manualmente sin revisar el cargo y la solicitud existente en Stripe. Ante timeout se conserva la misma solicitud y clave de idempotencia. Después de 23 horas con resultado desconocido solo se busca el reembolso existente; si no se encuentra, requiere revisión del operador para evitar reutilizar una clave expirada.

## Eventos y recuperación

El operador debe ejecutar el listener con estos eventos (y comprobar el secreto mostrado localmente):

```powershell
stripe listen --events checkout.session.completed,checkout.session.expired,refund.created,refund.updated,refund.failed --forward-to http://127.0.0.1:8000/pagos/stripe/webhook/
python manage.py reconcile_payments --limit 100
python manage.py reconcile_refunds --limit 100
```

El segundo conciliador revisa también devoluciones confirmadas para detectar rechazos bancarios posteriores si se perdió un evento. En local puede ejecutarse manualmente. Su programación operativa corresponde a la preparación del servidor; esta entrega no crea cron ni despliega. El listener anterior limitado a checkout no recibe los eventos refund.

Las firmas se validan antes de consultar el objeto canónico. Se comparan cargo, PaymentIntent, metadata de solicitud, moneda e importe completo. Refund no incluye `livemode` en su objeto: el cliente Stripe solo permite claves de pruebas, el webhook valida el modo del evento y la devolución debe corresponder al cargo verificado. Fuentes: [objeto Refund](https://docs.stripe.com/api/refunds/object), [fallos de devolución](https://docs.stripe.com/refunds#failed-refunds).

## Evidencia

- Reembolso real en la API sandbox de **599.51 MXN de prueba**, solicitado desde la nueva pantalla y confirmado por Stripe. Sin dinero real.
- Repetición de la solicitud conserva un solo registro. El evento real refund.created se recuperó de Stripe y se reprodujo localmente dos veces con firma válida: HTTP 200, un ProviderEvent, sin doble devolución. Esto no afirma entrega automática de ese evento por el listener anterior.
- Inventario completo conservado contra el respaldo inmediatamente anterior a estas migraciones: 92 registros, incluido el producto QA oculto. El producto QA permanece en stock 27/reservado 0. No se restauraron cambios previos del usuario detectados respecto de un respaldo más antiguo.
- Guía ficticia interna registrada mediante la vista administrativa y auditada; visible desde la cuenta de su propietario. No se compró etiqueta ni se envió un paquete real.
- Cuenta QA cerrada y desactivada de nuevo; contraseña temporal retirada. Operador QA sin permisos ni acceso al finalizar. Registros internos preservados para auditoría.
- Capturas locales ignoradas por Git en `artifacts/refund-qa/`: cancelacion-movil.png, reembolso-confirmado.png y seguimiento.png.
- Revisión independiente: corregida transición `succeeded → failed` y conciliación de confirmados; dos pruebas observaron RED y después GREEN. Sin otros hallazgos reportados.
- Suite final: **148 pruebas Django PASS**, incluida concurrencia de dos solicitudes sobre un mismo pedido. `manage.py check` sin incidencias y `makemigrations --check --dry-run` sin cambios. Las respuestas 400/403/404/500 que imprime la suite corresponden a pruebas deliberadas de las páginas de error.

## Revisión UI/UX

ui-ux-pro-max aplicado a confirmación explícita y feedback de acciones. Web Interface Guidelines consultadas durante esta implementación: `templates/orders/cancel.html`, `detail.html`, templates admin, `static/css/orders.css`, `static/js/checkout.js`. Confirmación semántica, checkbox etiquetado, CSRF, foco de error, mensajes accesibles, controles de al menos 44px, indicador al enviar y prevención de doble envío. Se conserva la alternativa de formulario sin JavaScript y movimiento reducido del sistema existente.

Cancelación inspeccionada en escritorio y 390px (botón de 51.6px de altura, sin desbordamiento). Seguimiento inspeccionado visualmente y medido sin overflow a 320, 844 y 1920px. Los números de guía largos se ajustan. No se cambió el hero ni la identidad visual.

## Antes de ventas reales

Validar empaques físicos con Jazmin, preparar claves y configuración live en una fase de activación explícita, configurar eventos y conciliación del servidor, y comprobar un recorrido operativo autorizado. El bloqueo a claves live sigue vigente. El portal propio de Jazmin corresponde al Módulo 3 y Gmail al Módulo 3.5; el despliegue lo realiza el usuario.
