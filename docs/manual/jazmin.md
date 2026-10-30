# Guía de operación para Jazmin

[Volver al manual](README.md) · MVP 1.0

Durante este MVP la operación se realiza en **Django admin**, en `/admin/`. El panel propio dentro del sitio llegará en el Módulo 3. Los nombres de algunas secciones o campos todavía pueden aparecer en inglés; esta guía incluye las rutas directas para localizarlos.

## 1. Acceso y rutina diaria

El responsable técnico te entrega una cuenta administrativa individual. Entra con el nombre de usuario administrativo y su contraseña; una cuenta registrada para comprar no obtiene estos permisos. Si falta una sección, solicita que revisen tus permisos. Cierra sesión al terminar en un equipo compartido.

Al comenzar la jornada:

1. Revisa pedidos nuevos y mensajes de WhatsApp.
2. Revisa cancelaciones antes de preparar piezas o generar guías.
3. Aprueba los diseños revisados o solicita ajustes con una nota clara.
4. Comprueba los pagos confirmados antes de producir y enviar.
5. Registra las guías y actualiza las entregas.
6. Actualiza las existencias si hubo entradas, daños o correcciones físicas.

No hay avisos automáticos por Gmail todavía. La revisión diaria del panel y WhatsApp es parte de la operación actual.

## 2. Revisar y aprobar pedidos

Abre **Orders → Orders** (`/admin/orders/order/`). Puedes buscar por referencia del pedido o correo del comprador y filtrar por estado de revisión y fecha.

1. Abre el pedido y revisa artículos, cantidades, notas y dirección.
2. Identifica su diseño recibido por WhatsApp usando la referencia del pedido. Los archivos PDF/PNG se comparten allí; no hay una bandeja de archivos adjuntos dentro del administrador.
3. Si el diseño está listo, en **Revisión del diseño** marca **Diseño revisado y aprobado por Jazmin** y pulsa **Guardar revisión**.
4. Si necesita ajustes, desmarca aprobación, marca **Solicitar cambios al cliente**, escribe lo necesario en **Nota visible para el cliente** y pulsa **Guardar revisión**. La nota es obligatoria al pedir cambios.
5. Para dejarlo pendiente, desmarca ambas opciones y guarda. No marques aprobar y solicitar cambios a la vez.

Las notas aparecen en la cuenta del cliente: escribe instrucciones útiles, sin información interna. Aprobar habilita el siguiente paso del comprador; **no cobra** ni acredita un pago. El historial conserva quién realizó la revisión.

Si otra persona ya cambió el pedido, recarga y revisa el nuevo estado antes de guardar. Si existe un pago en curso o confirmado, el sistema puede bloquear cambios de aprobación para conservar la operación. No modifiques la base de datos para saltar ese bloqueo.

Los pedidos conservan sus datos originales. Editar un producto o una dirección en otra pantalla no corrige un pedido ya creado; coordina cualquier error con el cliente y el responsable técnico antes de cobrar o enviar.

## 3. Consultar pagos

En **Payments → Payment attempts** (`/admin/payments/paymentattempt/`) busca la referencia del pedido. El resultado del proveedor determina el estado: no existe un botón para marcar manualmente «pagado».

- **Pagado / paid:** el pago se confirmó. Comprueba también que no haya una cancelación.
- **Abierto / open:** el cliente tiene una sesión pendiente de completar.
- **Creando / creating** o **requiere conciliación / reconciliation_required:** el resultado aún debe verificarse.
- **Vencido / expired** o **fallido / failed:** no es una confirmación de cobro.

Si el estado está desactualizado, selecciona el intento y ejecuta **Consultar estado de pago**. Si falla la consulta, conserva la referencia y pide apoyo técnico. **Expirar sesion y conciliar reserva** cierra una sesión pendiente: úsala solamente si has decidido que el cliente ya no debe continuar con esa sesión. No borres reservas ni intentes arreglar el resultado cambiando el inventario.

Algunos campos técnicos, como `total_minor` y `amount_minor`, se expresan en centavos: `18972` equivale a **$189.72 MXN**. Los importes mostrados al comprador ya están expresados en pesos.

## 4. Registrar guías y entregas

El MVP cotiza envíos pero **no compra ni genera etiquetas automáticamente**.

1. Comprueba que el pedido esté pagado y sin solicitud de cancelación.
2. Prepara el paquete y genera su guía directamente en Envia.
3. Abre el pedido en Django admin y localiza **Guía y seguimiento**.
4. Escribe transportista y número de guía. Puedes añadir un enlace público de seguimiento que empiece con `https://`; no copies un enlace de tu panel privado.
5. Marca **En camino** al entregar el paquete al transportista y pulsa **Guardar guía**.
6. Cuando confirmes la entrega, cambia a **Entregado** y guarda.

El comprador verá esos datos en **Mis pedidos**. El MVP maneja un registro de guía por pedido; no ofrece seguimiento separado para entregas parciales con varias guías. Si el caso requiere varios paquetes o una corrección de guía, coordínalo antes con el responsable técnico y el cliente.

## 5. Atender cancelaciones y devoluciones

Abre **Payments → Cancelaciones y reembolsos** (`/admin/payments/refund/`) y revisa también el aviso dentro del pedido.

La opción automática aplica antes de 24 horas desde el pago y con total pagado inferior a $2,000 MXN, incluyendo el envío. Devuelve el total al medio original. El MVP no añade una exclusión automática por producción o envío: revisa las solicitudes a tiempo para detener preparación y resolver en Envia cualquier guía ya comprada.

Selecciona la devolución y usa **Consultar / recuperar devolución en Stripe** si está pendiente o requiere revisión. No crees otra devolución manual sin comprobar la existente con el responsable técnico. Un fallo de comunicación no significa necesariamente que Stripe no la recibió.

**Reembolso confirmado** no garantiza que el banco ya lo muestre. Si después el proveedor informa un rechazo, el estado puede pasar a revisión. Atiende el caso con la referencia; no prometas una fecha de abono que no esté confirmada.

Las cancelaciones **no reponen stock automáticamente**. Revisa si las piezas realmente se pueden volver a vender antes de ajustar las existencias. Tampoco cancelan automáticamente una guía comprada en Envia.

## 6. Agregar o editar productos

Abre **Website → Products** (`/admin/website/product/`). Busca por nombre o SKU. Para crear uno, pulsa **Añadir**; para editar, abre su nombre.

| Campo | Qué registrar |
|---|---|
| `name`, `description` | Nombre y descripción que verá el cliente. |
| `slug` | Identificador de la dirección web. Evita cambiarlo en productos ya compartidos. |
| `category`, `technique_key` | Categoría y técnica. Los diseños sobre prendas negras son DTF. |
| `sku` | Código único: mayúsculas, números, puntos o guiones. No reutilices el de otra pieza. |
| `sale_mode` | **Precio fijo** para compra; **Cotización** para las excepciones del catálogo y las impresiones 3D personalizadas. |
| `price`, `currency` | Precio en pesos y moneda MXN. Un precio orientativo en cotización no convierte el artículo en venta directa. |
| `stock` | Existencias totales actuales del producto. Cero indica sin existencias; vacío no equivale a ilimitado. |
| `photo`, `image_alt` | Fotografía y una descripción breve de lo que muestra. |
| `is_concept` | Desmarcar para un producto real; los conceptos no se ofrecen como compra. |
| `is_active` | Marcar para publicar; desmarcar para retirar del catálogo. |
| `sort_order` | Los números menores aparecen primero. |

Guarda y comprueba la ficha pública. Antes de vender un producto nuevo, asigna también su **empaque de producto**; sin datos de empaque no se puede completar correctamente la cotización de envío.

Para retirar una pieza, desmarca `is_active` y conserva su historial. Evita eliminar productos que tengan pedidos, pagos o reservas relacionados.

### Existencias

El stock pertenece al producto completo, compartido entre los colores o detalles solicitados; no hay 30 unidades adicionales por cada variante. La inicialización de 30 unidades fue un punto de partida, no un valor que debas reponer periódicamente.

El sistema reserva unidades al preparar el pago y descuenta el stock cuando lo confirma. Por ejemplo: stock 30 y reserva 2 deja 28 disponibles; al pagar, queda stock 28 y se consume la reserva. No vuelvas a descontar esas 2 unidades manualmente.

Si el formulario avisa que las existencias cambiaron, recarga y compara antes de guardar. No puedes reducir el stock por debajo de las reservas activas.

### Fotografías y portada

Se admiten imágenes estáticas JPEG, PNG y WebP de hasta **5 MiB y 20 megapíxeles**. El sistema las optimiza a WebP, elimina metadatos y limita el lado mayor a 2400 px. No subas diseños privados de clientes como fotos del catálogo: estas imágenes son públicas.

Los paquetes comerciales se editan en `/admin/website/package/`. Los textos y fotos editables de portada están en `/admin/website/sitecontent/`, en un único registro. Conserva el fondo aprobado del hero salvo decisión expresa de cambiarlo. Guardar publica los cambios; no hay una vista previa editorial separada.

## 7. Empaques para el cálculo de envío

En **Shipping → Perfiles de caja** (`/admin/shipping/packageprofile/`) se definen largo, ancho y alto en **centímetros**, peso de la caja vacía y peso máximo en **kilogramos**, y capacidad.

En **Shipping → Empaques de productos** (`/admin/shipping/productpacking/`) se asigna cada producto a una caja, su peso unitario protegido y las unidades de capacidad que ocupa. Los productos compatibles se agrupan; el cálculo no equivale a comprar una guía por unidad.

Los valores iniciales son provisionales. Mide y pesa muestras reales con protección antes de confirmarlos. Usa **Confirmar medidas y capacidad revisadas** solamente después de la comprobación física. Cambiar datos operativos retira esa validación y exige revisarlos otra vez.

## 8. Usuarios y permisos

El responsable autorizado gestiona usuarios en `/admin/auth/user/`. Para bloquear un acceso, identifica primero la cuenta correcta y desmarca **Activo**, conservando pedidos e historial. Un nombre interno largo puede corresponder a una cuenta de comprador: comprueba el correo y el perfil, no te guíes solo por ese identificador.

No concedas **staff** o **superusuario** a compradores. El alta de operadores y sus permisos se detalla en el [anexo técnico](operacion-tecnica.md). Las cuentas de acceso deben ser individuales.

## 9. Cuándo pedir apoyo técnico

Si aparece un error repetido, un pago no se concilia, una devolución requiere revisión o no puedes guardar una guía, anota la referencia del pedido, la hora y el mensaje exacto. Adjunta una captura sin contraseñas, tarjetas ni claves. No borres el pedido para intentar corregirlo.

Antes de cambios masivos en catálogo o existencias, solicita un respaldo de base y fotografías. Los [respaldos y recuperación](operacion-tecnica.md) corresponden al responsable técnico.
