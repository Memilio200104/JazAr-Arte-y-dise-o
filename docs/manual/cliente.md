# Guía para compradores

[Volver al manual](README.md) · MVP 1.0

## 1. Elegir una pieza

Explora el catálogo desde la página de inicio. Los productos de **precio fijo** abren su ficha: revisa descripción, precio, cantidad y detalles de personalización antes de agregarlos al carrito. Los productos **por cotización**, incluidas las impresiones 3D personalizadas, llevan al contacto con Jazmin.

Las indicaciones de talla, color o diseño se revisan con Jazmin; escribirlas no garantiza por sí solo su disponibilidad. Los diseños sobre prendas negras corresponden a DTF.

El carrito está en `/carrito/`. Es una selección guardada en ese navegador: no reserva piezas ni garantiza que aparezca en otro dispositivo. Los pedidos ya solicitados sí quedan asociados a tu cuenta.

## 2. Crear tu cuenta y guardar una dirección

1. Abre **Crear cuenta** (`/cuenta/registro/`). Escribe nombre completo, correo y contraseña, y confirma la contraseña.
2. Para volver, usa **Ingresar** (`/cuenta/ingresar/`) con correo y contraseña.
3. En **Mi cuenta → Direcciones de envío**, pulsa **Agregar dirección**.
4. Completa quién recibe, teléfono, calle, número exterior, colonia, código postal de cinco dígitos, municipio o alcaldía y estado. Interior y referencias son opcionales. Las entregas del sitio son en México.
5. Puedes guardar varias direcciones y elegir **Usar como predeterminada**. Revisa la dirección seleccionada al crear cada pedido.

Cambiar o borrar una dirección guardada no modifica la copia de dirección de un pedido existente. Si te equivocaste en un pedido, avisa a Jazmin antes de pagar o preparar el envío.

La recuperación de contraseña está en `/cuenta/recuperar/`. En el entorno actual los enlaces de recuperación y verificación se generan en la consola del servidor, no llegan por Gmail: solicita ayuda al responsable técnico. La cuenta del comprador no da acceso a `/admin/`.

## 3. Solicitar revisión del diseño

1. Desde el carrito, continúa con la selección. Inicia sesión si se solicita.
2. Elige una dirección y escribe las notas necesarias.
3. Pulsa **Revisar resumen**. Comprueba artículos, cantidades, subtotal y dirección. Usa **Editar detalles** si necesitas corregir algo.
4. Pulsa **Solicitar revisión**. Conserva la referencia del pedido.
5. En el detalle, pulsa **Enviar diseño por WhatsApp** y adjunta el archivo **PDF o PNG**. El enlace incluye la referencia para identificar el pedido.

Crear la solicitud no cobra ni reserva existencias. El costo de envío se calcula después de la aprobación. La referencia del pedido permite coordinar los cambios sin crear solicitudes repetidas.

## 4. Consultar la aprobación

Abre **Mi cuenta → Mis pedidos** (`/cuenta/pedidos/`) y entra al detalle del pedido. Puedes consultar las solicitudes desde cualquier dispositivo ingresando en la misma cuenta.

| Estado | Qué hacer |
|---|---|
| En revisión | Envía el archivo por WhatsApp si aún falta y espera la revisión. |
| Cambios solicitados | Lee la **Nota de Jazmin** y envía los ajustes por WhatsApp. |
| Diseño aprobado | Pulsa **Elegir envío y pagar**. |
| Pago pendiente | Continúa con el pago existente. |
| Verificando pago / Preparando pago | Consulta su estado; no crees otro pedido para pagar de nuevo. |
| Sesión vencida / Pago no completado | Abre la página de pago y sigue las opciones para consultar o reintentar. |
| Pago confirmado | El cobro quedó registrado; ya no necesitas pagar otra vez. |
| En camino / Entregado | Revisa los datos de seguimiento del pedido. |

Los avisos por correo se añadirán en el Módulo 3.5. De momento consulta esta sección y WhatsApp.

## 5. Elegir envío y pagar

1. Con el diseño aprobado, abre la página de pago del pedido.
2. Pulsa **Calcular envío** (la interfaz puede mostrar «Calcular envio») y espera las opciones disponibles para tu dirección y paquete.
3. Elige el servicio. **Terrestre** es el nombre que usamos para servicios identificados como `ground` por la paquetería.
4. Revisa subtotal, envío y total en MXN. La cotización puede vencer o cambiar; confirma el nuevo importe si el sitio lo solicita.
5. Pulsa **Ir al pago** y completa el formulario alojado en Stripe.
6. Al regresar, comprueba el estado. Si aún no se confirma, utiliza **Actualizar estado**. Volver desde Stripe no equivale por sí solo a un pago confirmado.

Si cerraste Stripe sin terminar, usa la opción para retomar el pago del mismo pedido. No envíes datos de tarjeta por WhatsApp. En la entrega local se utilizan exclusivamente pagos de prueba indicados por el responsable técnico.

El sitio cobra el envío dentro del mismo pago. No ofrece recogida como opción de checkout; cualquier acuerdo de recogida se trata directamente con Jazmin por WhatsApp.

## 6. Ver el seguimiento

Una vez registrada la guía, abre **Mis pedidos → Ver pedido → Seguimiento del envío**. Verás transportista, número de guía y estado. Si Jazmin incluyó un enlace público, aparecerá **Rastrear envío**.

Los estados **En camino** y **Entregado** los actualiza Jazmin manualmente. El sitio todavía no sincroniza todos los movimientos de la paquetería; consulta su enlace o utiliza el número de guía en el sitio del transportista.

## 7. Solicitar una cancelación

La cancelación disponible en el MVP exige ambas condiciones:

- Solicitarla **antes de cumplir 24 horas desde el pago confirmado**.
- Que el **total pagado, incluido el envío, sea menor a $2,000 MXN**. Un total de $2,000 exactos no entra en esta opción.

En el detalle de un pedido elegible pulsa **Solicitar cancelación**, revisa importe y plazo, marca la confirmación y envía la solicitud. Se solicita la devolución completa al mismo medio de pago; el tiempo para verla reflejada depende del banco.

| Estado de la cancelación | Significado |
|---|---|
| Cancelación solicitada | La solicitud quedó registrada; se está consultando la devolución. |
| Reembolso en proceso | La devolución sigue pendiente. Consulta su estado desde la misma solicitud. |
| Reembolso confirmado | Stripe confirmó la devolución; el banco puede tardar en reflejarla. |
| Reembolso requiere revisión | Contacta a Jazmin con la referencia del pedido. No solicites otro cobro o devolución por tu cuenta. |

Si la opción no aparece, revisa el plazo, el total y si ya existe una cancelación. Contactar a Jazmin permite revisar el caso, pero no cambia automáticamente estas condiciones.

## 8. Resolver dudas frecuentes

| Situación | Acción |
|---|---|
| No veo mi pedido | Comprueba que ingresaste con el mismo correo con el que lo solicitaste. |
| Aparece 403 o un formulario no se envía | Vuelve a cargar la página y abre de nuevo el formulario. Si persiste, comunica la ruta y hora del error al responsable técnico. |
| No puedo entrar al administrador | El acceso de comprador y el acceso administrativo tienen permisos diferentes. Para comprar usa `/cuenta/ingresar/`. |
| No hay opciones de envío | Revisa dirección y código postal. Si persiste, contacta a Jazmin; puede faltar cobertura, configuración o datos del paquete. |
| Stripe parece haber cobrado pero el pedido sigue pendiente | Consulta **Actualizar estado** y reporta la referencia. No repitas el pago mientras se revisa. |
| No llega un correo | Gmail está pendiente del Módulo 3.5; en local solicita apoyo técnico. |

Para contactar: [WhatsApp de JazAr, 55 3975 4777](https://wa.me/525539754777) o [Facebook de JazAr](https://www.facebook.com/profile.php?id=100084852678555). Comparte referencia y descripción del problema; nunca contraseña ni datos completos de tarjeta.
