# Envios agrupados y Checkout: estado de implementacion

Actualizado el 27 de octubre de 2026. Plan: docs/superpowers/plans/2026-10-25-shipping-checkout.md. Especificacion aprobada con agrupacion de productos. Ejecucion directa en la carpeta y rama existentes; no despliegue.

## Implementado

- Perfiles de caja y asignaciones por producto en Django Admin: dimensiones exteriores, tara, peso bruto maximo, capacidad y peso unitario protegido. Validacion administrativa con autor/fecha; cambios operativos invalidan la confirmacion.
- Agrupacion determinista de unidades compatibles en cajas compartidas; capacidad/peso pueden generar varias cajas. No es optimizacion geometrica ni garantiza el minimo numero de cajas.
- Envia sandbox: POST /ship/rate/ por transportista, paquetes completos, normalizacion de totalPrice MXN a centavos, errores recuperables, limite por cliente y cache privada. Cotizacion copiada al pedido; cambios de empaques invalidan seleccion. Recotizacion antes de pagar y confirmacion adicional si cambia el importe.
- Existencias disponibles = stock fisico - reservado. Reserva atomica al iniciar pago; solo pago confirmado consume stock. Formularios admin obsoletos no pueden restaurar existencias ya vendidas.
- Stripe SDK 16.0.0 y API 2026-09-30.endive, Checkout alojado, tarjetas, solo sk_test_. Payload persistido/clave idempotente por intento. Webhook firmado y conciliacion verifican referencia, sesion, entorno, moneda e importe.
- Aprobacion no revocable mientras exista pago activo/pagado. Expirar y conciliar primero desde Pagos en admin. No hay aprobacion del comprador.
- Pantalla privada /pedido/<uuid>/pago/: direccion, piezas, servicio, total y redireccion Stripe; retorno muestra estado real y permite actualizar via POST. Sin avisos publicos de demo. Interfaz funcional sin JS; no guarda tarjetas.

## Empaques provisionales

`seed_shipping_profiles` no escribe por defecto; `--apply` crea solo registros faltantes. Tres cajas:

| Perfil | Dimensiones cm | Tara kg | Maximo kg | Capacidad |
| --- | --- | --- | --- | --- |
| Textiles | 35 x 25 x 20 | 0.250 | 5 | 6 |
| Tazas protegidas | 35 x 25 x 20 | 0.350 | 5 | 4 |
| Voluminosos | 50 x 40 x 35 | 0.700 | 10 | 4 |

31 productos identificados tienen asignaciones provisionales: textiles 0.350 kg/unidad y tazas 0.550 kg/unidad, ocupacion 1. Los pesos incluyen proteccion individual; la tara de caja se suma una vez. Los demas productos se asignan desde /admin/shipping/productpacking/ cuando se conozca su acomodo; no deducir medidas de una foto ni asumir que tazas para pareja equivalen a una sola taza.

Jazmin debe validar cajas, acomodos y pesos antes de ventas reales. Una capacidad declarada no prueba que objetos fisicamente quepan. No mezclar perfiles incompatibles. Productos sin asignacion activa no cotizan. No se modifican fotos, precios ni hero.

## Configuracion y recorrido

1. Crear cuentas sandbox de Envia y Stripe. Guardar claves solo en .env usando nombres de .env.example. No usar claves live: esta entrega las rechaza.
2. Revisar origen configurado (CP 55710) y codigos de direccion aceptados por el proveedor. El origen no ha sido validado externamente.
3. Iniciar Django en 8000 y Stripe CLI listener segun README; establecer secreto de firma del listener y reiniciar Django.
4. Comprador crea solicitud; Jazmin revisa el diseno por WhatsApp y aprueba desde /admin/orders/order/.
5. Desde Mis pedidos, abrir el pedido y Envio y pago. Elegir envio, revisar total, continuar a Stripe con tarjeta de prueba. Comprobar webhook, detalle y stock.
6. Probar rechazo, abandono, expiracion, reintento, y `python manage.py reconcile_payments --limit 100`. No liberar reservas por reloj local ni por regresar con cancel_url.

Permisos staff: orders.view_order + orders.approve_order para revision. Para pagos: payments.view_paymentattempt + payments.reconcile_payment. Datos de pagos/reservas son solo lectura; no se marca pagado a mano. Acciones administrativas consultan Stripe y conservan reservas ante incertidumbre.

## Decisiones de implementacion

- Se conserva el checkout actual por solicitud expresa del usuario, sin worktree.
- Solo SKU explicitamente identificados reciben asignacion provisional; costo: productos restantes no pueden cotizar hasta configurarse.
- Envia se consulta por transportista (hasta tres) siguiendo su Core Workflow; endpoint fijo de sandbox. No hay fallback a produccion.
- Reserva local de 30 minutos; Stripe recibe expiracion a 31 minutos para tolerar latencia frente a su minimo de 30. La liberacion exige expiracion confirmada, por lo que puede durar algo mas si Stripe no responde.
- Si una creacion tuvo resultado desconocido, un rechazo posterior no prueba que no exista sesion: conserva reserva. Tras 23 horas sin resolver, requiere revision administrativa en Stripe. Costo: temporalmente menos stock disponible, evitando sobreventa.
- Solo POST explicito Actualizar estado y webhook concilian; el GET de retorno no muta pagos. Costo: sin webhook el comprador debe actualizar el estado.
- Envia no declara expiracion en el ejemplo de tarifas consultado: vigencia local maxima 10 minutos y recotizacion obligatoria; no se garantiza el precio futuro de una guia.

## Revision y verificaciones

Revision independiente recibida de review_shipping_payments: tres hallazgos corregidos y cubiertos por pruebas: guardado obsoleto restauraba stock, rechazo definitivo de creacion retenia reserva, constraint SQL permitia stock null con reservas. Se verificaron nuevamente tras retomar. Una prueba adicional reprodujo la liberacion indebida tras resultado desconocido y ahora pasa. Prueba concurrente que fallaba por upgrade de locks SQLite corregida adquiriendo lock de escritura antes de leer.

UI: ui-ux-pro-max aplicado a recuperacion/foco de errores. Web Interface Guidelines consultadas el 27 de octubre: templates/payments/checkout.html, static/js/checkout.js y static/css/orders.css revisados en etiquetas, foco, radios, feedback, controles tactiles y movimiento reducido. Capturas de 390 y 1440px inspeccionadas; checkout sin overflow a 320/390/844/1440/1920px y alternativa sin JS verificadas.

Verificacion final local: 119 pruebas Django PASS; 2 pruebas concurrentes con SQLite de archivo PASS; check_checkout, check_accounts, check_orders, check_store y test_cart_state PASS. `manage.py check` sin incidencias, `makemigrations --check --dry-run` sin cambios, `git diff --check` limpio salvo advertencias CRLF. No sustituir estos resultados por las pruebas externas pendientes.

## Persistencia y pendientes

Respaldo previo inicial: runtime/backups/before-checkout-20261027-085009.sqlite3. Respaldo antes de las correcciones finales: runtime/backups/before-checkout-fixes-20261027-163133.sqlite3. Migraciones aplicadas; 91 productos y 1 pedido existente conservados; cero intentos de pago y cero unidades reservadas en la base principal. Fixtures navegador solo en runtime/accounts-browser.sqlite3.

Pendiente para aceptacion: credenciales y recorrido real de sandbox Envia/Stripe; no se han realizado solicitudes externas con datos de compradores. Faltan asignaciones/validacion de empaques restantes, operacion de guias y detalles finales de cancelacion/reembolso. No hay compra de guias, reembolsos automaticos, cobros live, despliegue ni Gmail operativo. El Modulo 2 no se declara listo para produccion.

Referencias: https://docs.envia.com/docs/core-workflow ; https://docs.envia.com/docs/ecommerce-checkout ; https://docs.stripe.com/api/checkout/sessions/create ; https://docs.stripe.com/api/idempotent_requests ; https://docs.stripe.com/webhooks .
