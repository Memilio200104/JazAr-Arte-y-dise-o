# Pedidos y aprobacion de diseno

Estado: especificacion aprobada por el usuario. Implementacion pendiente de revision del plan.

## Objetivo y decisiones confirmadas

Convertir la seleccion del comprador en una solicitud persistente que Jazmin pueda consultar y aprobar en Django Admin despues de revisar el PDF/PNG por WhatsApp. El cliente consulta su pedido y nunca puede aprobarlo. El pago exige aprobacion del servidor, no una declaracion del navegador.

Cuenta obligatoria. Existencias iniciales: 30 por producto, compartidas entre tallas y colores. Cotizaciones y piezas 3D personalizadas quedan fuera. Gmail y panel administrativo propio del sitio pertenecen al Modulo 3. No modificar el hero ni desplegar.

## Alternativas y eleccion

1. Recomendada y aprobada: Django Admin para aprobacion; misma logica reutilizable desde el futuro panel del sitio. Menos superficie nueva y permisos existentes.
2. Panel propio ahora: duplica trabajo reservado para Modulo 3.
3. Checkbox del comprador: no acredita la revision de Jazmin; descartado.

## Limites de este bloque

Incluye creacion, listado y detalle privados de solicitudes; copia de direccion; lineas y precios; revision administrativa y trazabilidad. No incluye Stripe, cotizador de envios, reservas, reembolsos, produccion, expedicion ni correos nuevos. No crea credenciales administrativas compartidas ni convierte la cuenta de prueba del comprador en staff.

La aprobacion del diseno es necesaria, pero no suficiente para cobrar. Mientras falten tarifa de envio e integracion de pago, mostrar "Diseno aprobado; pago aun no disponible", sin un enlace de cobro ficticio. El siguiente bloque del Modulo 2 integrara envio y pago, revalidando aprobacion, precio, disponibilidad y vigencia de la tarifa.

## Modelo y responsabilidades

Nueva app `orders`, sin reemplazar auth ni catalogo:

- Order: identificador publico UUID, propietario protegido contra borrado accidental, fecha de creacion/actualizacion, moneda MXN, subtotal decimal, copia estructurada de direccion y datos del destinatario, notas del comprador limitadas a 1500 caracteres, estado de revision, aprobador y fecha, clave de idempotencia.
- OrderItem: pedido, producto con PROTECT, copia de SKU/nombre/precio unitario, cantidad entera positiva, detalles de talla/color solicitados como texto acotado. Son instrucciones por revisar, no variantes con disponibilidad garantizada. Total calculado con Decimal.
- OrderReviewEvent: pedido, actor, estado anterior/nuevo, fecha y nota publica de revision. Historial solo lectura, sin borrado desde admin.
- Estados de revision: pendiente, cambios solicitados y aprobado. No inventar estados pagado o enviado sin sus subsistemas.

Las copias de lineas y direccion no cambian al editar catalogo o agenda. Productos con pedidos se desactivan en vez de borrarse. El estado y los datos comerciales de pedidos no son editables libremente en admin; las transiciones pasan por un servicio atomico.

## Flujo del comprador

1. Mantener el carrito actual de IDs/cantidades en el navegador. Continuar lleva a solicitud, con ingreso obligatorio y retorno a esa ruta.
2. Seleccionar una direccion propia guardada. Sin direcciones, ofrecer creacion y conservar el carrito. No obligar a verificar correo durante pruebas locales; esto no garantiza la propiedad del correo para la futura compra.
3. Recalcular productos y subtotal en servidor y presentar resumen antes de confirmar. El navegador no decide precios, propietario ni estados.
4. Enviar POST CSRF con clave de idempotencia, direccion, IDs/cantidades y detalles. Maximo 100 lineas distintas, 99 unidades por linea y disponibilidad actual como limite adicional. Rechazar IDs duplicados, cantidades no enteras, productos inactivos/cotizados/conceptos o stock desconocido. Mostrar errores sin perder la seleccion.
5. Si precio/disponibilidad cambia entre resumen y confirmacion, pedir revisar el resumen actualizado; nunca aceptar un cambio de importe silencioso.
6. Crear pedido y lineas en una transaccion; repetir el mismo envio devuelve el pedido existente del mismo propietario. Reutilizar la clave con datos distintos se rechaza. Limpiar solo la seleccion enviada tras exito, no ante error.
7. Detalle muestra referencia, piezas, subtotal, direccion, estado y nota de Jazmin. Enlace WhatsApp con referencia del pedido, sin direccion ni otros datos personales en la URL. PDF/PNG se envia por WhatsApp; no implementar subida ni integracion automatica.
8. Mi cuenta incluye historial real y estado vacio. Listado y detalle filtran por propietario: UUID no sustituye autorizacion. Respuestas privadas no-store.

## Aprobacion en Django Admin

Listado de todos los pedidos para personal con permiso: fecha, referencia, comprador, subtotal y estado; busqueda por referencia y correo, filtros por estado/fecha. Detalle con lineas y direccion de solo lectura.

Checkbox "Diseno revisado y aprobado por Jazmin", con etiqueta asociada y aspecto nativo del admin para esta fase. Guardar aplica la transicion solo con permiso dedicado `orders.approve_order`, usuario activo y staff. No conceder ese permiso al grupo de compradores. Superusuarios conservan su acceso habitual.

Marcar aprueba y registra usuario/fecha; guardar sin cambiar estado no reemplaza esos datos ni crea eventos duplicados. Desmarcar revoca y vuelve a pendiente, dejando evento. Solicitar cambios exige nota visible al cliente y revoca aprobacion. Operaciones concurrentes usan version esperada: una revision obsoleta pide recargar en vez de sobrescribir otra decision. Error de persistencia conserva el estado previo e informa que se debe reintentar.

La futura API de pagos consultara el estado persistido cada vez. La revocacion con sesiones de pago abiertas necesitara coordinacion con Stripe en el bloque de pagos; no se simula resuelta aqui.

## Inventario y precios: propuesta para este bloque

Una solicitud en revision NO reserva ni descuenta existencias y se informa al cliente. Aprobar el diseno tampoco garantiza stock. La reserva atomica y su vencimiento se disenan con el pago para no bloquear inventario indefinidamente por solicitudes impagadas.

Preparar comando explicito de inicializacion a 30 para productos reales de precio fijo cuyo stock este sin definir, con vista previa y reporte de cantidades. No restablecer valores existentes ni conceptos/cotizaciones, ni reponer en cada migracion. Respaldar la base antes de aplicarlo. Cualquier valor existente distinto de 30 se conserva y se reporta para decision del propietario.

Guardar precio de referencia aceptado al solicitar revision; no es un total final cobrado. No hay cambios de precio del pedido desde admin en esta fase. El checkout futuro debera definir vigencia y reconfirmacion antes de cobrar.

## Interfaz y accesibilidad

Reutilizar templates Django, iconos Lucide y sistema visual actual. Sin nueva libreria. Resumen legible, estado textual (no solo color), botones con foco visible, errores asociados a campos, controles tactiles de 44 px, navegacion por teclado. Transiciones cortas de opacidad/transform solo donde aporten feedback; respetar movimiento reducido. No incluir checkbox de aprobacion en pantallas de cliente.

Comprobar 320, 390, 844, 1440 y 1920 px, especialmente panel estrecho de Codex; conservar modo sin JavaScript con aviso y ruta al catalogo, sin fingir que se puede importar localStorage sin JS. Aplicar ui-ux-pro-max y revision vigente de web-design-guidelines al implementar.

## Seguridad y pruebas de aceptacion

- POST anonimo no crea pedidos; un cliente no puede leer pedidos/direcciones ajenas ni enviar aprobacion, actor, precio o estado propios.
- CSRF, limites de payload, idempotencia y concurrencia de envios probados. Aplicar limite persistente por cliente a creacion: 10 solicitudes nuevas por 15 minutos; reintento idempotente no consume otra solicitud. Fallos del limitador cierran la operacion.
- Validar cantidades, stock y elegibilidad; rollback sin pedidos incompletos; errores de base recuperables.
- Copias de direccion/precio permanecen tras edicion de sus origenes; productos historicos protegidos contra borrado.
- Revision staff autorizada, denegacion sin permiso, auditoria, revocacion, nota requerida y conflicto de version.
- Detalle de pago no revela pedidos ajenos y permanece bloqueado sin aprobacion y sin integracion real.
- Pruebas Django, navegador con DB aislada, regresiones del sitio y revision independiente antes de cierre; nunca crear pedidos ficticios entre los datos del cliente.

## Entrega y temas separados

Migraciones con respaldo y verificacion de catalogo/usuarios. Documentar rutas y operacion administrativa, commit/push en rama actual; sin merge ni despliegue. Metodo previamente elegido: ejecucion directa en carpeta actual, no worktree.

Antes del bloque de pagos se resolveran proveedor y origen de envios, embalajes, vigencia de tarifas, reservas, inicio/base de cancelacion y reembolsos. No se usan estas decisiones pendientes para inventar reglas en este bloque de revision.
