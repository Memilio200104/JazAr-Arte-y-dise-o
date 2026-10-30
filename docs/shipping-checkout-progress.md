# Envios agrupados y Checkout: estado de implementacion

Actualizado el 28 de octubre de 2026. Plan: docs/superpowers/plans/2026-10-25-shipping-checkout.md. Especificacion aprobada con agrupacion de productos. Ejecucion directa en la carpeta y rama existentes; no despliegue.

**Estado vigente al 30 de octubre:** el recorrido de pago sandbox se verifico con proveedores el 29 de octubre. Cancelacion con devolucion completa y seguimiento manual de guias ya estan implementados; consultar [operacion y evidencia actual](cancellations-tracking.md). Los pendientes externos citados en las secciones historicas inferiores se sustituyen por ese estado. Se conserva el bloqueo a cobros reales y la validacion fisica de empaques pendiente.

## Implementado

- Perfiles de caja y asignaciones por producto en Django Admin: dimensiones exteriores, tara, peso bruto maximo, capacidad y peso unitario protegido. Validacion administrativa con autor/fecha; cambios operativos invalidan la confirmacion.
- Agrupacion determinista de unidades compatibles en cajas compartidas; capacidad/peso pueden generar varias cajas. No es optimizacion geometrica ni garantiza el minimo numero de cajas.
- Envia sandbox: POST /ship/rate/ por transportista, paquetes completos, normalizacion de totalPrice MXN a centavos, errores recuperables, limite por cliente y cache privada. Cotizacion copiada al pedido; cambios de empaques invalidan seleccion. Recotizacion antes de pagar y confirmacion adicional si cambia el importe.
- Existencias disponibles = stock fisico - reservado. Reserva atomica al iniciar pago; solo pago confirmado consume stock. Formularios admin obsoletos no pueden restaurar existencias ya vendidas.
- Stripe SDK 16.0.0 y API 2026-09-30.endive, Checkout alojado, tarjetas, solo sk_test_. Payload persistido/clave idempotente por intento. Webhook firmado y conciliacion verifican referencia, sesion, entorno, moneda e importe.
- Aprobacion no revocable mientras exista pago activo/pagado. Expirar y conciliar primero desde Pagos en admin. No hay aprobacion del comprador.
- Pantalla privada /pedido/<uuid>/pago/: direccion, piezas, servicio, total y redireccion Stripe; retorno muestra estado real y permite actualizar via POST. Sin avisos publicos de demo. Interfaz funcional sin JS; no guarda tarjetas.

## Empaques provisionales

`seed_shipping_profiles` no escribe por defecto; `--apply` crea solo registros faltantes y conserva ediciones y validaciones existentes. Ocho cajas provisionales:

| Perfil | Dimensiones cm | Tara kg | Maximo kg | Capacidad |
| --- | --- | --- | --- | --- |
| Textiles | 35 x 25 x 20 | 0.250 | 5 | 6 |
| Tazas protegidas | 35 x 25 x 20 | 0.350 | 5 | 4 |
| Voluminosos | 50 x 40 x 35 | 0.700 | 10 | 4 |
| Termos y vasos | 40 x 30 x 35 | 0.500 | 10 | 6 |
| Articulos planos | 45 x 35 x 18 | 0.450 | 8 | 6 |
| Accesorios | 35 x 25 x 25 | 0.300 | 5 | 6 |
| Enrollados | 40 x 20 x 20 | 0.300 | 5 | 4 |
| Globo protegido | 60 x 60 x 60 | 0.600 | 3 | 1 |

Los 79 productos de precio fijo del catalogo tienen asignaciones provisionales; se excluyen cotizaciones y conceptos. Se conservaron las 31 asignaciones originales y se agregaron 48. Los pesos incluyen proteccion individual; la tara de caja se suma una vez. Los SKU y valores iniciales completos estan en shipping/management/commands/seed_shipping_profiles.py y son editables desde /admin/shipping/productpacking/.

Una unidad vendida representa el producto completo: el par de tazas ocupa 2 espacios y pesa 1.100 kg; los juegos de 4/6 portavasos pesan 0.200/0.300 kg por juego. Se supone que textiles y cojines pueden plegarse, el mousepad de teclado se enrolla y el globo viaja inflado en caja individual. Estos son supuestos de desarrollo autorizados, no medidas obtenidas de fotos ni certificacion de acomodo. Jazmin debe confirmar especialmente marcos, fragiles, cojines y globos. Productos futuros o SKU desconocidos requieren configuracion explicita; no reciben una caja generica automaticamente.

Jazmin debe validar cajas, acomodos y pesos antes de ventas reales. Una capacidad declarada no prueba que objetos fisicamente quepan. No mezclar perfiles incompatibles. Productos sin asignacion activa no cotizan. No se modifican fotos, precios ni hero.

## Configuracion y recorrido

1. Crear cuentas sandbox de Envia y Stripe. Guardar claves solo en .env usando nombres de .env.example. No usar claves live: esta entrega las rechaza.
2. Revisar origen configurado (CP 55710) y codigos de direccion aceptados por el proveedor. El origen no ha sido validado externamente.
3. Iniciar Django en 8000 y Stripe CLI listener segun README; establecer secreto de firma del listener y reiniciar Django.
4. Comprador crea solicitud; Jazmin revisa el diseno por WhatsApp y aprueba desde /admin/orders/order/.
5. Desde Mis pedidos, abrir el pedido y Elegir envio y pagar. Elegir envio, revisar total, continuar a Stripe con tarjeta de prueba. Comprobar webhook, detalle y stock.
6. Probar rechazo, abandono, expiracion, reintento, y `python manage.py reconcile_payments --limit 100`. No liberar reservas por reloj local ni por regresar con cancel_url.

Permisos staff: orders.view_order + orders.approve_order para revision. Para pagos: payments.view_paymentattempt + payments.reconcile_payment. Datos de pagos/reservas son solo lectura; no se marca pagado a mano. Acciones administrativas consultan Stripe y conservan reservas ante incertidumbre.

## Decisiones de implementacion

- Se conserva el checkout actual por solicitud expresa del usuario, sin worktree.
- Solo SKU explicitamente identificados reciben asignacion provisional; los 79 actuales estan cubiertos. Costo: nuevos SKU no pueden cotizar hasta configurarse.
- Envia se consulta por transportista (hasta tres) siguiendo su Core Workflow; endpoint fijo de sandbox. No hay fallback a produccion.
- Reserva local de 30 minutos; Stripe recibe expiracion a 31 minutos para tolerar latencia frente a su minimo de 30. La liberacion exige expiracion confirmada, por lo que puede durar algo mas si Stripe no responde.
- Si una creacion tuvo resultado desconocido, un rechazo posterior no prueba que no exista sesion: conserva reserva. Tras 23 horas sin resolver, requiere revision administrativa en Stripe. Costo: temporalmente menos stock disponible, evitando sobreventa.
- Solo POST explicito Actualizar estado y webhook concilian; el GET de retorno no muta pagos. Costo: sin webhook el comprador debe actualizar el estado.
- Envia no declara expiracion en el ejemplo de tarifas consultado: vigencia local maxima 10 minutos y recotizacion obligatoria; no se garantiza el precio futuro de una guia.

## Revision y verificaciones

Revision independiente recibida de review_shipping_payments: tres hallazgos corregidos y cubiertos por pruebas: guardado obsoleto restauraba stock, rechazo definitivo de creacion retenia reserva, constraint SQL permitia stock null con reservas. Se verificaron nuevamente tras retomar. Una prueba adicional reprodujo la liberacion indebida tras resultado desconocido y ahora pasa. Prueba concurrente que fallaba por upgrade de locks SQLite corregida adquiriendo lock de escritura antes de leer.

UI: ui-ux-pro-max aplicado a recuperacion/foco de errores. Web Interface Guidelines consultadas el 27 de octubre: templates/payments/checkout.html, static/js/checkout.js y static/css/orders.css revisados en etiquetas, foco, radios, feedback, controles tactiles y movimiento reducido. Capturas de 390 y 1440px inspeccionadas; checkout sin overflow a 320/390/844/1440/1920px y alternativa sin JS verificadas.

Verificacion final local: 119 pruebas Django PASS; 2 pruebas concurrentes con SQLite de archivo PASS; check_checkout, check_accounts, check_orders, check_store y test_cart_state PASS. `manage.py check` sin incidencias, `makemigrations --check --dry-run` sin cambios, `git diff --check` limpio salvo advertencias CRLF. No sustituir estos resultados por las pruebas externas pendientes.

### Continuacion: catalogo completo y progreso de pedidos (28 de octubre)

- Mis pedidos y detalle comparten un presentador de estados: revision, cambios solicitados, diseno aprobado, preparando pago, pago pendiente, sesion vencida, pago no completado, verificando pago y pago confirmado. Aprobacion nunca equivale a cobro. No se infiere expiracion por reloj local.
- Cada estado explica el siguiente paso. Tras pago confirmado se muestra el total cobrado con envio y acceso a Ver pago; desaparecen las instrucciones de reenviar el diseno o volver a pagar. Las notas historicas de Jazmin se conservan como contexto del pedido.
- UI UX Pro Max: estado comunicado con texto e icono ademas de color. Web Interface Guidelines consultadas el 28 de octubre: templates/orders/list.html, detail.html, status.html y static/css/orders.css revisados; enlaces semanticos, iconos decorativos, foco visible heredado, controles de 44/48px, saltos de texto, movimiento reducido y estados vacios conservados. Formato monetario localizado con Django para es-MX, sin dependencia de JS. Sin hallazgos pendientes en este alcance.
- Seis pruebas nuevas observadas RED antes de implementar y GREEN despues: cobertura de 79 productos, pares/juegos, idempotencia y preservacion de ediciones, estados de revision/pago y vistas pagadas privadas. Suite completa: **125 pruebas PASS**. Check, migraciones pendientes y diff-check sin errores.
- check_checkout y check_orders PASS: 320/390/844/1440/1920px sin overflow, detalle/lista pagados, aprobacion administrativa, carrito concurrente y alternativa sin JS. Capturas de lista 1440px y detalle 390px inspeccionadas. Las credenciales de proveedores se desactivan explicitamente en config.test_accounts_browser para mantener las fixtures aisladas aunque cambie .env.
- Revision independiente review_catalog_order_status: ningun hallazgo critico, importante o menor. Se ratifica que acomodo fisico y aceptacion externa se validan despues; cancelaciones y despliegue quedan fuera del cambio. Se actualizaron los conteos antes diferidos por el revisor. Conservar notas previas de Jazmin es intencional; no cambian el CTA del pago confirmado.

## Persistencia y pendientes

Respaldo previo inicial: runtime/backups/before-checkout-20261027-085009.sqlite3. Respaldo antes de las correcciones finales: runtime/backups/before-checkout-fixes-20261027-163133.sqlite3. Migraciones aplicadas; 91 productos y 1 pedido existente conservados; cero intentos de pago y cero unidades reservadas en la base principal. Fixtures navegador solo en runtime/accounts-browser.sqlite3.

La continuacion se aplico despues del respaldo runtime/backups/before-catalog-packing-20261028-173953.sqlite3: 91 productos, 79 asignaciones y cero productos fijos sin empaque. Se conservaron los 3 pedidos locales actuales y cero intentos de pago. No se modificaron precios ni existencias.

Pendiente para aceptacion: credenciales y recorrido real de sandbox Envia/Stripe; no se han realizado solicitudes externas con datos de compradores. Falta validacion fisica de empaques, operacion de guias y detalles finales de cancelacion/reembolso. No hay compra de guias, reembolsos automaticos, cobros live, despliegue ni Gmail operativo. El Modulo 2 no se declara listo para produccion.

Referencias: https://docs.envia.com/docs/core-workflow ; https://docs.envia.com/docs/ecommerce-checkout ; https://docs.stripe.com/api/checkout/sessions/create ; https://docs.stripe.com/api/idempotent_requests ; https://docs.stripe.com/webhooks .

## Primera conexion sandbox verificada (28 de octubre)

- ENVIA_TOKEN autentica correctamente en sandbox; se realizo una cotizacion del pedido local aprobado y se recibieron cinco opciones MXN de DHL/Estafeta. No se compro ninguna guia ni se persistio esa cotizacion diagnostica.
- La llamada con el agente HTTP predeterminado Python-urllib respondia 403; identificacion explicita JazAr/1.0 obtuvo respuesta valida. El adaptador ahora declara ese User-Agent.
- La direccion guardada tenia estado `Mex.` con acento; se reconocen Mex., Mexico, Edomex y EM como Estado de Mexico, conservando Ciudad de Mexico como CX. No se cambia la direccion guardada.
- STRIPE_TOKEN contenia una clave privada de pruebas: se traslado localmente a STRIPE_SECRET_KEY. Stripe acepto una consulta de solo lectura a Checkout Sessions. STRIPE_TOKEN_PUBLIC se conserva, pero el Checkout alojado no necesita la clave publica. No se crearon sesiones ni cargos en esta comprobacion.
- STRIPE_WEBHOOK_SECRET sigue pendiente. Por ello la validacion de pago completo, webhook y stock sigue sin completarse; la presencia de claves no equivale a aceptacion integral.
- Regresiones observadas RED antes de corregir y GREEN despues; 58 pruebas shipping/payments/orders PASS. .env permanece excluido de Git; no se registraron claves en documentacion ni comandos de salida.

Esta comprobacion sustituye la ausencia total de credenciales anotada en los cortes anteriores; siguen pendientes los pasos restantes de aceptacion, validacion fisica de empaques y operacion.

Continuacion del 28 de octubre: etiquetas de servicios en espanol, indicadores de carga y secreto de webhook comprobado localmente. Ver [estado de carga y cierre](checkout-loading-status.md). La firma local pasa; la entrega Stripe CLI y el pago integral siguen pendientes.
