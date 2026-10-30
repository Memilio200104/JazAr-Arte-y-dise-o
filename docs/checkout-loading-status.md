# Servicios legibles e indicadores de carga

28 de octubre de 2026. Solicitud directa: mostrar ground como terrestre y dar feedback cuando el sitio o las operaciones tardan.

## Cambios

- `ShippingQuote.service_label` presenta ground como Terrestre, ground_od como Terrestre · OD, express como Expres con acento y local como Local. OD se conserva como identificador de variante, sin inventar tiempos de entrega. El codigo original sigue almacenado y se usa al recotizar.
- Opciones y resumen usan la etiqueta traducida. Nuevas sesiones de Stripe usan la misma etiqueta; payloads ya persistidos no se reescriben para conservar la idempotencia.
- Indicador global compacto, sin bloquear contenido ni controles: carga inicial de recursos, navegacion interna y formularios nativos. Aparece tras 220 ms para evitar parpadeos; no inventa porcentajes. No puede aparecer antes de que el navegador reciba y ejecute el HTML/JS inicial.
- Cotizacion, resumen, pago, reintento y actualizacion muestran mensajes especificos y spinner en el boton. El valor de la accion se conserva en un input antes de deshabilitar el boton. Un segundo submit se rechaza.
- Al volver atras se restauran botones, estado busy y mensajes, respetando controles que ya estaban deshabilitados. Se ignoran enlaces externos, otras pestanas, descargas, anclas y formularios cancelados o invalidos.
- Mensajes con role=status, iconos decorativos y movimiento reducido. Escape descarta el indicador global; a los 12 segundos avisa de demora y se oculta 8 segundos despues para no quedar permanente ante una navegacion cancelada. No altera precios ni pedidos.

## Verificacion

- Etiquetas y nombre del envio en Stripe: pruebas observadas RED y luego GREEN. Suite Django: 127 PASS.
- `scripts/check_loading.cjs` PASS: recurso inicial lento, formulario invalido, spinner de checkout y action preservada, recuperacion pageshow, navegacion diferida, movimiento reducido y funcionamiento sin JS. El evento de submit de la fixture se despacha sin navegacion para inspeccionar el DOM; `check_checkout` verifica POSTs reales contra la base aislada.
- `check_checkout` PASS: checkout privado, error honesto sin claves, cinco anchos, pedidos pagados y sin JS. Captura de carga inicial a 390 px inspeccionada.
- UI UX Pro Max consultado para loading feedback; Web Interface Guidelines consultadas para contraste, regiones de estado, movimiento reducido y controles. Ninguna pantalla de bloqueo ni retraso minimo artificial para mostrar la animacion.
- Django check sin incidencias; makemigrations --check --dry-run sin cambios.
- check_orders PASS: solicitud, aprobacion/revocacion administrativa y carrito concurrente en cinco anchos. Revision independiente review_shipping_labels_loading sin hallazgos. Limites: pageshow se simula, no se prueba restauracion BFCache real; la navegacion lenta se completa pero esa prueba no afirma visibilidad del indicador durante el cambio de documento. Si se detecta diferencia entre navegadores, reproducirla antes de ampliar el comportamiento.

## Configuracion de webhook y cierre de Modulo 2

El secreto local existe y coincide con Stripe CLI autenticado. Tras recargar Django, un evento diagnostico firmado y sin pedido asociado devuelve 200; una firma invalida devuelve 400. Esta prueba no cambia pedidos y no demuestra entrega desde Stripe.

En la primera verificacion no se dejo un listener activo: la revision automatica bloqueo su arranque con `blocked by policy`, sin razon mas especifica. El 29 de octubre el operador lo inicio y se verifico entrega de eventos de pago y vencimiento; ver [pruebas de proveedores](provider-acceptance-2026-10-29.md). Para pruebas locales el operador debe mantener abierto en su terminal:

```powershell
stripe listen --events checkout.session.completed,checkout.session.expired,refund.created,refund.updated,refund.failed --forward-to http://127.0.0.1:8000/pagos/stripe/webhook/
```

Pago sandbox, entrega de webhook, consumo de stock, rechazo, abandono y reintento verificados el 29 de octubre. Cancelacion/reembolso y registro manual de guias implementados en la continuacion; ver [operacion y evidencia](cancellations-tracking.md). El operador debe ampliar el listener para incluir los eventos refund. Validacion fisica de empaques antes de ventas reales. El despliegue corresponde al usuario; Gmail y panel propio de Jazmin siguen en Modulo 3.
