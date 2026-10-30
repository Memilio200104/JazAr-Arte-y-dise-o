# Verificacion de Envia y Stripe en sandbox

29 de octubre de 2026. Pruebas autorizadas sobre la instalacion local, sin cobros reales ni creacion de guias.

## Correccion encontrada

La API fijada a `2026-09-30.endive` rechazo la creacion de Checkout con HTTP 400: `payment_method_types` ya no esta admitido. Se cambio a `allowed_payment_method_types=['card']`, conservando la restriccion a tarjeta. No se reescriben payloads de intentos anteriores ni sus claves de idempotencia.

Referencia oficial: [Crear Checkout Session](https://docs.stripe.com/api/checkout/sessions/create), parametro `allowed_payment_method_types`. Las tarjetas utilizadas son las de la [documentacion de pruebas](https://docs.stripe.com/testing).

## Resultados observados

- Envia sandbox devolvio tarifas reales de su API; el importe elegido se recotizo antes de abrir Stripe. Checkout mostro `DHL · Terrestre`.
- Tarjeta de rechazo: Stripe mostro el error; el intento local siguio abierto, stock 30 y reserva 2. No se marco como pagado.
- Reintento con tarjeta aceptada: Stripe confirmo 599.51 MXN de prueba. Durante esa prueba el servidor y el listener anteriores ya no estaban activos. Tras levantar Django, el boton **Actualizar estado** recupero la confirmacion: stock 28, reserva 0. Esto verifica recuperacion manual, no entrega automatica de ese evento.
- El operador volvio a iniciar Stripe CLI. En un segundo pedido, salir de Checkout dejo el pago pendiente. Retomar un intento abierto reutilizo su sesion.
- Se expiro la segunda sesion mediante la API oficial, sin actualizar su estado local desde el script. El webhook `checkout.session.expired` llego al servidor y libero la reserva: stock 28, reserva 0. No se espero el vencimiento natural de 30 minutos.
- El mismo pedido pudo iniciar un nuevo intento. El pago de 189.72 MXN de prueba se confirmo automaticamente mediante `checkout.session.completed`: retorno del navegador con **Pago confirmado**, stock 27 y reserva 0, sin pulsar Actualizar estado.
- Se recupero ese evento real y se reprodujo dos veces contra el endpoint local con firma valida: ambas respuestas 200, un solo `ProviderEvent` y sin nuevo descuento de existencias. La reproduccion fue local; no se simulo que Stripe hubiera reenviado el evento.

Los importes anteriores corresponden solo a estas cotizaciones sandbox; no son tarifas publicas fijas.

## Datos y evidencias

Se genero respaldo SQLite antes de las pruebas. Se usaron una cuenta, un producto y dos pedidos internos. El producto permanecio oculto al catalogo mediante transacciones; al terminar la cuenta quedo desactivada y sin contraseña utilizable. No quedan reservas o intentos abiertos de estos registros.

Se conservaron intactos el stock/estado de los 91 productos anteriores, la revision/version de los 3 pedidos existentes y los 3 intentos previos, que ya estaban fallidos. Los registros internos se conservan para auditoria: no producir ni enviar sus piezas.

Evidencias locales ignoradas por Git: `artifacts/provider-qa/pago-confirmado.png` y `artifacts/provider-qa/pago-webhook-confirmado.png`. Referencias y respaldo en `runtime/provider-qa.json`; no contiene contraseña al cierre. No se versionan credenciales ni URLs de sesiones de pago.

## Validacion del cambio

- Regresion observada RED antes del cambio y GREEN despues: payload compatible con Endive y restringido a tarjeta.
- 32 pruebas del paquete payments pasan despues de la correccion. Suite completa anterior a la correccion: 127 pruebas pasan.
- Django check sin incidencias; makemigrations --check --dry-run sin cambios.
- Revision del diff: cambio limitado al parametro de nuevas sesiones. Se conserva el flujo de aprobacion, los importes, las firmas y la idempotencia. Esta fase no modifica templates, estilos ni interacciones.

## Pendientes del Modulo 2

La integracion sandbox de cotizacion, cobro y webhooks tiene evidencia de extremo a extremo. Cancelaciones y seguimiento quedaron definidos y se implementaron en la continuacion: ver [cancelaciones y seguimiento](cancellations-tracking.md), incluida devolucion de los 599.51 MXN de prueba. Validar empaques fisicos antes de ventas reales. No habilitar claves live ni desplegar por esta verificacion. El panel propio de Jazmin corresponde al Modulo 3 y Gmail al Modulo 3.5.
