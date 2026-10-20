# JazAr: frontend del e-commerce

Fecha: 19 de octubre de 2026.
Estado: especificacion aprobada por el usuario; plan de implementacion pendiente de revision y eleccion de ejecucion.

## Objetivo y limites

Construir el recorrido visual de compra antes de implementar el backend transaccional. Usar el catalogo real y la identidad actual, con paginas Django navegables, interacciones locales y estados honestos. No presentar el sitio como una demo.

Esta entrega no crea cuentas de compradores, pedidos, reservas, cotizaciones de transporte, cobros ni reembolsos. No instala Stripe ni integra proveedores. Las vistas de lectura necesarias para servir templates y consultar productos forman parte de esta entrega. Gmail y despliegue siguen aplazados.

Se recomienda continuar con templates Django y JavaScript progresivo: aprovecha los modelos, imagenes y estilos existentes sin duplicar el catalogo. Una maqueta separada duplicaria trabajo; implementar simultaneamente backend contradice la prioridad aprobada.

## Reglas confirmadas

- Precio fijo abre detalle de producto; cotizacion conserva el contacto. Las excepciones son las marcadas en el catalogo y la impresion 3D personalizada.
- Las prendas negras se presentan como DTF segun la clasificacion existente. No reclasificar ceramica negra automaticamente.
- Cuenta obligatoria para comprar cuando se conecte el backend.
- Diseno por WhatsApp, PDF o PNG, aprobado por Jazmin antes del cobro.
- Envio dinamico cobrado en la web. No ofrecer recogida en checkout ni asumir envio gratis.
- Existencias iniciales solicitadas: 30. Esta etapa no migra stock ni inventa disponibilidad individual.
- Stripe en etapa posterior y modo pruebas inicial. No pedir datos de tarjeta en formularios propios.

## Pantallas y rutas propuestas

1. `/productos/<slug>/`: detalle para productos activos, no conceptuales, de precio fijo con precio definido. Imagen real ampliable, nombre, precio MXN, descripcion, tecnica, nota comercial y cantidad. No inventar variantes ni fotografias; si existe una sola imagen, no mostrar miniaturas repetidas. Los SKU distintos permanecen productos distintos.
2. `/carrito/`: seleccion local, cantidades editables, eliminar, subtotal y estado vacio. Envio indicado como pendiente de calcular, nunca como cero. Acceso al siguiente paso mediante cuenta.
3. `/cuenta/ingresar/`, `/cuenta/registro/`, `/cuenta/recuperar/`: formularios accesibles con estados visuales de validacion; sin enviar ni almacenar credenciales. Acciones de autenticacion deshabilitadas con explicacion breve de disponibilidad, sin mensaje de exito.
4. `/pedido/solicitud/`: composicion visual de resumen, direccion e instrucciones para entregar diseno. Sin crear un pedido ni una referencia ficticia. Los campos no persisten datos personales y el envio definitivo permanece deshabilitado.
5. `/cuenta/`: composicion de cuenta y pedidos con estado sin sesion. No mostrar una identidad ni pedidos inventados como reales.
6. `/pedido/pago/`: composicion de resumen, envio y pago bloqueada hasta aprobacion. No cotizar, cobrar ni mostrar importe de envio supuesto.

Las pantallas posteriores a autenticacion tendran acceso para revision mediante un indice de desarrollo disponible solo con DEBUG, fuera del menu publico. Los estados de pedido (en revision, cambios solicitados, aprobado, pendiente de pago) se podran inspeccionar alli con fixtures exclusivamente visuales claramente identificados como ejemplos; no seran pedidos del usuario. No crear un mecanismo que finja una sesion iniciada.

Las rutas definitivas podran conservarse al conectar el backend; en ese momento se aplicaran permisos de cuenta y propiedad de pedido antes de exponer datos reales.

## Interacciones sin backend

- Imagen y enlace principal de cada ficha fija abren su detalle. Cotizaciones usan el contacto de portada con el interes seleccionado.
- Agregar al carrito opera exclusivamente sobre una seleccion del navegador. Guardar en localStorage solo identificadores y cantidades; nunca direccion, contrasenas, aprobaciones o datos de pago.
- La lectura del catalogo determina nombre y precio actual; no confiar en precios almacenados. El futuro backend recalculara todo de forma autoritativa.
- Cantidades enteras positivas, limites conservadores de interfaz y validacion de datos locales corruptos. Stock conocido cero impide agregar; stock desconocido no se presenta como disponibilidad garantizada.
- Un producto desactivado, eliminado o cambiado a cotizacion no permanece comprable en la seleccion. Informar del ajuste sin romper la pagina.
- No permitir continuar como invitado. La falta de autenticacion real no se sustituye por una cuenta falsa.
- WhatsApp y Facebook existentes siguen funcionando. No generar mensajes que afirmen que existe un pedido cuando solo hay una seleccion.
- Sin JavaScript, el catalogo y los detalles permanecen legibles y el contacto funciona; indicar la necesidad de JavaScript para la seleccion local.

## Direccion visual

Conservar tipografia local, fondos claros y oscuros, acentos cian y magenta, iconos Lucide y lenguaje visual existente. No adoptar una nueva paleta generica.

Detalle de producto con fotografia protagonista y bloque de compra sin tarjeta decorativa exterior. En escritorio, dos columnas; en movil, imagen y datos apilados. Resumen lateral en escritorio y despues del contenido en movil. No usar scroll secuestrado ni parallax en campos y resumenes.

Transiciones cortas de opacidad y transformacion, feedback al agregar, apertura de imagen y actualizacion de cantidades. Respetar reduced-motion. Los fondos animados no reducen contraste ni capturan eventos. Mantener controles estables, foco visible, etiquetas explicitas, objetivos tactiles de al menos 44 px y estados anunciados con moderacion.

La navegacion incorpora accesos reconocibles a carrito y cuenta, contador de seleccion local y retorno al catalogo. El encabezado no oculta titulos ni mensajes.

## Retirar la presentacion como demo

- Retirar etiquetas publicas de demo y referencias comerciales obsoletas.
- Actualizacion expresa del usuario durante implementacion: conservar el fondo original hero-concept.webp en portada; no sustituirlo por la fotografia del taller. Mantener alt descriptivo de composicion conceptual sin etiqueta publica de demo.
- Mientras Gmail no este conectado, explicar de forma breve que el correo no esta disponible y ofrecer WhatsApp; no afirmar que un mensaje llego a Jazmin.
- Mantener documentacion tecnica veraz sobre funcionalidades pendientes.
- Conservar migraciones historicas, comandos de compatibilidad y referencias tecnicas necesarias como `--hide-demo`; renombrarlos indiscriminadamente podria romper instalaciones. No reescribir historial Git.

## Organizacion tecnica

Reutilizar Product, SiteContent, assets locales y base.html. Extraer navegacion compartida de forma acotada si es necesario para las nuevas paginas, conservando anclas funcionales desde rutas internas.

Separar templates de tienda, estilos comerciales y JavaScript de seleccion de la logica de animaciones de portada. Usar vistas GET de lectura, rutas nombradas y componentes para precio, resumen y estados. No introducir modelos transaccionales ni endpoints POST falsos.

No modificar configuracion productiva, secretos ni el administrador privado. Las paginas de revision y fixtures no se exponen con DEBUG=False.

## Verificacion y aceptacion

- Pruebas Django: rutas, elegibilidad de producto, 404 de productos no publicados, enlaces de cotizacion, ausencia de endpoints transaccionales y aislamiento de fixtures.
- Pruebas de navegador: detalle desde catalogo, seleccion, persistencia local, cantidades, eliminar, vacio, datos corruptos y producto no elegible.
- Revisar 320, 390, 768, 844, 1024, 1440 y 1920 px de ancho, incluyendo alturas reducidas. Sin desbordamiento horizontal, controles ocultos ni regresion del proceso creativo.
- Teclado, foco, ampliacion de imagen, reduced-motion, sin JavaScript, imagenes cargadas y errores de consola.
- Revisar con ui-ux-pro-max y las Web Interface Guidelines vigentes; registrar resultados y capturas.
- Ejecutar suite existente ademas de las nuevas pruebas. No afirmar que autenticar, comprar, cotizar transporte o pagar funcionan hasta implementar sus integraciones.

## Entrega y siguiente etapa

Entregar frontend navegable localmente y documentar pantallas e integraciones pendientes. No desplegar.

El proveedor de envios, origen y embalajes, politicas precisas de cancelacion, inventario compartido y expiracion de reservas se resolveran en la especificacion posterior del backend. No son valores a inventar para completar estas pantallas.

Tras aprobar este documento, preparar el plan de implementacion y elegir su forma de ejecucion antes de modificar codigo de producto.
