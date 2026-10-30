# Envios y pago con Stripe Checkout

Estado: aprobado por el usuario con agrupacion de productos por envio. 25 de octubre de 2026.

Revision independiente inicial completada: sin preguntas importantes pendientes. Correccion posterior solicitada por el usuario: agrupar productos, no cotizar un paquete por unidad. No se ha implementado el bloque.

## Intencion y decisiones recibidas

Completar el recorrido del comprador desde un pedido aprobado hasta un pago confirmado, conservando cuentas, direccion e historial existentes. No desplegar ni activar cobros reales.

- Envia.com elegido para comenzar, sin cuenta o credenciales disponibles aun.
- Stripe Checkout alojado elegido por el usuario: salir a Stripe y volver a JazAr.
- Solo Jazmin/personal autorizado aprueba desde Django Admin; no permitir autoaprobacion del comprador.
- Empaques provisionales autorizados para desarrollar y probar pagos completos. Jazmin proporcionara los definitivos.
- Sin etiquetas de demo/prueba en la interfaz publica de JazAr. No ocultar indicadores de pruebas que Stripe presente.
- Origen confirmado en docs/modulo-2-requisitos.md: Villa de las Flores, Coacalco, Mexico, CP 55710.
- Solo envios; recogida fuera del sitio. Existencias compartidas por producto, no por talla/color. Gmail y portal staff propio quedan en Modulo 3.

## Alternativas y alcance

Se considero Checkout alojado (menos mantenimiento, redireccion externa) y formulario integrado (continuidad visual, mayor mantenimiento). El usuario eligio alojado. No almacenar ni procesar numeros de tarjeta en Django.

Dividir la implementacion en envios, reservas y pagos, con contratos comunes. Esta propuesta cubre cotizacion y cobro del envio, no compra automatica de guias ni seguimiento logistico. La emision de guias debe resolverse antes de produccion; no confundir pago confirmado con envio despachado.

Fuera de este bloque: descuentos, impuestos calculados dinamicamente, OXXO/transferencias o medios de confirmacion diferida, reembolsos automaticos, politica final de cancelacion, notificaciones Gmail y despliegue. La regla comercial de 24 horas/menos de 2000 permanece pendiente de precisar antes de activar ventas reales; no publicar una interpretacion inventada.

## Diseno aprobado y decisiones de implementacion

### Empaques y cotizaciones

Crear perfiles de caja editables en admin: codigo, nombre, dimensiones exteriores en cm, tara en kg, peso bruto maximo, capacidad entera, activo, validado y fecha/autor de validacion. Por producto, registrar peso unitario protegido, perfil compatible y unidades de capacidad ocupadas. Semillas provisionales explicitas y reversibles solo donde falte perfil; nunca sobrescribir ajustes de Jazmin. Valores concretos a elegir durante implementacion, marcados internos como provisionales.

Agrupar unidades de productos compatibles en cajas compartidas hasta alcanzar capacidad o peso bruto maximo; abrir otra caja solo cuando sea necesario. Decision tecnica: reglas de capacidad declaradas por perfil, no simulacion geometrica 3D ni suma de dimensiones. Una unidad debe caber individualmente en el perfil declarado. No mezclar perfiles incompatibles (por ejemplo, fragiles sin proteccion compatible). Las reglas de capacidad representan acomodos que Jazmin debe validar; los provisionales solo sirven en sandbox. No se promete el numero matematicamente minimo de cajas.

Algoritmo determinista first-fit decreasing por capacidad ocupada, peso y producto id; cada caja conserva dimensiones exteriores del perfil y peso tara + suma de pesos unitarios protegidos. El mismo pedido/configuracion produce los mismos paquetes. Copiar composicion por caja para trazabilidad. Agrupar distintos productos si comparten perfil, respetar cantidades y limites, y rechazar unidades que excedan por si solas capacidad/peso. No truncar cantidades ni omitir productos.

Cotizar todas las cajas del envio juntas; si el servicio no soporta la cantidad resultante, no ofrecer esa tarifa. Los limites del proveedor se validan antes de consultar. Productos sin perfil activo no pueden cotizarse. Cambios de pesos, capacidades, asignaciones o dimensiones invalidan la cotizacion anterior, pero no alteran snapshots de sesiones de pago abiertas.

ShippingQuote conserva propietario/pedido, direccion y paquetes copiados, revision de configuracion, servicio/transportista, moneda, importe final en centavos, referencia del proveedor y vencimiento. Precios exclusivamente del servidor y respuesta validada del proveedor. Solo MXN y destinos Mexico inicialmente; excluir respuestas incompletas, moneda distinta o importes invalidos. Sin tarifa ficticia de respaldo ni envio gratis implicito.

Propuesta: vigencia local maxima de 10 minutos, acortada si el proveedor declara una menor; es una politica del sitio, no una garantia de precio del transportista. Al iniciar Checkout recotizar siempre el servicio seleccionado. Si cambia el total, mostrar resumen actualizado y pedir otra confirmacion. Una vez abierta la sesion, su importe queda fijo; no ajustar cobros sin consentimiento.

Adapter Envia separado de reglas de negocio, con timeouts, respuestas normalizadas, rate limit por usuario y cache corta por huella de solicitud. Credenciales solo servidor, sin volcarlas ni registrar domicilios completos. Sandbox por defecto. Datos de contacto del remitente configurables; usar los datos comerciales ya confirmados cuando sean aceptados por el proveedor. No asumir que el CP equivale a validar el domicilio.

### Reserva de existencias

Solicitar revision no reserva stock. Abrir Checkout reserva las cantidades de todos los productos de forma atomica mediante actualizaciones condicionales, compatible con SQLite. Modelar reservas aparte: disponible = stock - reservas activas; no descontar stock fisico dos veces. El admin no puede reducir stock por debajo de unidades reservadas sin resolverlas.

Un intento activo por pedido; doble clic devuelve la misma sesion. Duracion propuesta: 30 minutos. La fecha local sola no autoriza liberar una reserva: consultar/expirar la sesion de Stripe y confirmar su estado terminal. Si Stripe no responde, conservar la reserva y permitir reconciliacion posterior, no sobreventa. Una compra confirmada consume stock y reserva una sola vez dentro de transaccion.

El comando de reconciliacion se ejecutara manualmente en local y quedara documentado para ejecucion periodica por el operador en produccion. Tambien reconciliar al reintentar el pago. No requiere Celery en este bloque.

### Pago y consistencia

PaymentAttempt guarda UUID, pedido, revision aprobada, cotizacion copiada, total MXN, clave idempotente, session id unico, expiracion y estado creating/open/paid/expired/failed/reconciliation_required. Persistir intento y reserva antes de la llamada externa; no mantener transaccion DB mientras se espera la red. Timeout de creacion es resultado desconocido: recuperar con la misma clave, no crear otro intento ni liberar stock a ciegas.

Checkout mode payment, tarjetas inicialmente, importe calculado de OrderItem y envio seleccionado. Conservar los precios copiados al solicitar revision; no sustituir silenciosamente por precio nuevo del catalogo. Antes de reservar revalidar productos activos, stock, aprobacion, cuenta activa y direccion/configuracion. El subtotal del pedido no cambia por consultar tarifas. No permitir editar direccion o articulos de un pedido aprobado en este bloque: nueva solicitud si necesita cambiarlos.

Bloquear cambios del estado de aprobacion mientras haya intento de pago abierto o confirmado. Para devolver un pedido abierto a revision, primero expirar la sesion y reconciliar: si ya fue pagada, no revocar la aprobacion y marcar para gestion administrativa. Notas pueden editarse conservando autor y fecha originales de aprobacion. Historial visible y permisos separados; nunca marcar pagado desde un checkbox.

La vuelta del navegador no confirma pagos. Webhook firmado y consulta autenticada a Stripe comparten una funcion idempotente que verifica session id, pedido, entorno, moneda, total y payment_status. Registrar evento unico y aplicar transicion atomica; duplicados/desorden no consumen stock de nuevo ni degradan paid. Importe/entorno inesperado pasa a reconciliacion, no a pedido listo. Los eventos fallidos deben ser reintentables, no marcados procesados antes de completar la transaccion.

El retorno de cancelacion de Stripe significa volver al pedido, no cancelar/reembolsar la compra ni liberar reserva automaticamente. Mostrar estado real y opcion para retomar una sesion abierta. Para confirmacion pendiente usar mensaje de procesamiento, nunca exito optimista.

### Experiencia y acceso

Reutilizar /pedido/<uuid>/pago/ para direccion resumida, opciones de envio con radios, productos/subtotal/envio/total y boton Ir al pago. Cuenta obligatoria, ownership en cada endpoint, POST con CSRF para mutaciones, datos privados no-store. El webhook es la unica excepcion CSRF y exige firma Stripe.

Mis pedidos y detalle muestran revision, pago pendiente/en proceso/confirmado por separado. Sin redisenar hero o navegacion. Conservar estilos magenta y controles existentes, foco visible, areas tactiles >=44px, errores accionables, estados accesibles y movimiento reducido. Revisar con ui-ux-pro-max y web-design-guidelines durante implementacion. Verificar 320, 390, 844, 1440 y 1920px, navegacion por teclado y alternativa sin JS.

Sin credenciales, las paginas pueden mostrar un error honesto de pago/envio no disponible y permitir reintentar; no simular exito publico. Fixtures/fakes solo en tests automatizados aislados. La prueba integral real requiere cuentas sandbox y claves de Envia/Stripe, ademas del webhook local. No afirmar validacion integral hasta completarla.

### Configuracion y seguridad de lanzamiento

Modo pruebas explicito por defecto, SDK oficial Stripe con version fijada tras consultar documentacion. Rechazar credenciales/eventos live en esta entrega. Activacion real sera otro cambio controlado despues de validar empaques, politicas, operacion de guias y credenciales; no bastara cambiar una clave .env accidentalmente.

Origen, contactos y secretos en configuracion servidor; documentar nombres en .env.example sin valores sensibles. URL de retorno desde origen configurado, no del Host enviado por el cliente. Guardar referencias minimas de proveedores, sin tarjetas ni secretos. Sin correos de produccion, compra de guias, cargos reales o despliegue.

## Pruebas y entrega

- Migraciones reversibles cuando sea viable, respaldo SQLite antes de migrar la base principal; no generar pedidos ficticios alli.
- Tests de propiedad, aprobacion, moneda/importes manipulados, tarifas vencidas/cambiadas, errores del proveedor y falta de perfiles.
- Concurrencia de ultimo stock, doble clic, timeout de creacion, liberacion segura, webhook duplicado/desordenado, retorno falso y firma incorrecta.
- Revisar efectos en catalogo, carrito, admin, solicitudes y cuentas; suite existente completa mas pruebas nuevas.
- Verificacion visual responsive y accesibilidad de estados nuevos, sin modificar el hero.
- Recorrido sandbox con tarjetas de prueba: exito, rechazo, abandono, expiracion y retorno. Si faltan claves, documentar ese pendiente claramente.
- Actualizar README y ledger con comandos de webhook/reconciliacion, configuracion, resultados y bloqueos reales. Revision independiente antes de cerrar implementacion.

## Referencias oficiales consultadas

- https://docs.stripe.com/payments/checkout
- https://docs.stripe.com/api/checkout/sessions/create
- https://docs.stripe.com/checkout/fulfillment
- https://docs.envia.com/docs/getting-started

Consultar los detalles vigentes de cada endpoint y SDK al escribir el plan. Esta especificacion no afirma que las integraciones ya existan.
