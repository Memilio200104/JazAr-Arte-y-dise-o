# Contenido editable del Modulo 1

## Objetivo

Jazmin o una persona autorizada puede sustituir conceptos por productos y fotos reales, editar paquetes y los textos principales sin modificar codigo. Se conserva el sitio publico, su identidad y sus animaciones. No se necesita contenido definitivo para desarrollar y verificar este flujo.

## Alcance y decisiones

Se utilizara Django Admin para administracion interna. Es preferible a construir un CMS propio: reutiliza permisos, formularios, CSRF y registro de cambios existentes en Django. No se agrega un CMS externo ni un segundo frontend.

El acceso administrativo no equivale al login de compradores. Solo usuarios activos con permisos de staff pueden entrar; los permisos por modelo restringen la edicion. No habra registro publico de administradores ni credenciales predeterminadas. Un operador crea el primer superusuario desde terminal. Habilitar validadores de contrasena de Django y documentar HTTPS como condicion de publicacion.

## Datos

### Productos

Conservar Product, sus identificadores, SKU, precio nullable, moneda, stock nullable, categoria, tecnica y orden. Conservar image como ruta de respaldo para conceptos existentes. Agregar fotografia opcional y texto alternativo. Una propiedad image_url resuelve fotografia cargada o recurso static; los templates dejan de suponer que todas las imagenes pertenecen a static.

is_active mantiene su significado de publicacion. Nuevos productos se crean no publicados; una migracion no modifica el estado de los existentes. is_concept controla los avisos de referencia por producto: una fotografia real no debe etiquetarse automaticamente como concepto. Para publicar una fotografia se exige texto alternativo. No se exige precio para solicitar cotizacion.

### Paquetes

Crear Package con slug unico, nombre, descripcion, inclusiones, texto del enlace, interes de contacto limitado a opciones validas, icono de un conjunto permitido, is_active y sort_order. Sin HTML libre ni iconos suministrados como markup. Conservar los tres paquetes iniciales mediante migracion de datos, sin sobrescribir ediciones posteriores.

### Contenido de la portada

Crear SiteContent como registro unico editable. Campos: encabezado y descripcion del hero; titulo y texto de presentacion; titulo y texto de contacto; nombre y firma profesional; enlace Facebook validado como HTTPS. Incluir imagenes opcionales de hero y presentacion con textos alternativos. El nombre de marca se conserva como H1; no se permite inyectar HTML, CSS ni JavaScript.

La estructura, botones de navegacion y cinco etapas del proceso permanecen en templates en esta entrega. La edicion de textos no promete editar libremente el diseno completo. Los textos iniciales se conservan como valores de respaldo si aun no existe SiteContent.

## Publicacion y administracion

Listas de productos y paquetes con busqueda, filtros por publicacion y tecnica cuando aplique, orden y miniaturas. Formularios agrupados en contenido, imagen, publicacion y datos comerciales futuros. Guardar borrador conserva el registro fuera del sitio publico; publicar hace visible su contenido al siguiente GET. No hay versionado editorial ni vista previa publica de borradores en esta entrega.

SiteContent se edita directamente; no se agrega un sistema de revisiones para la portada. El admin impide crear un segundo registro y no ofrece eliminacion del unico registro desde la interfaz. No se modifica la base local del usuario para crear contrasenas o usuarios sin comunicarselo.

## Archivos y persistencia

Aceptar JPEG, PNG y WebP; rechazar SVG, HTML, archivos corruptos y animaciones. Limite de 5 MiB por archivo y 20 megapixeles decodificados. Verificar con Pillow y recodificar a WebP con nombre aleatorio, quitando metadatos y evitando depender del nombre original. Limitar el lado mayor a 2400 px y conservar proporcion. Aplicar validacion tambien fuera del formulario administrativo mediante el servicio de procesamiento de imagenes.

MEDIA_ROOT sera runtime/media y MEDIA_URL /media/. El volumen runtime_data ya persistente se conserva; Nginx monta ese volumen en solo lectura y sirve unicamente su subdirectorio media, nunca SQLite, logs ni cache. En desarrollo Django sirve media solo con DEBUG. Ambas configuraciones HTTP y HTTPS se actualizan, con nosniff y limite de carga coherente con los formularios. No permitir ejecucion de archivos cargados.

Los medios son publicos: no cargar material confidencial ni propuestas privadas. Reemplazar una foto no borra automaticamente el archivo anterior; facilita recuperacion. Respaldar base de datos y medios conjuntamente antes de despliegue. No introducir eliminacion automatica de archivos en esta entrega.

## Compatibilidad visual

Imagenes de producto en contenedor estable con object-fit:cover; hero y presentacion mantienen sus proporciones y alternativas actuales. Textos largos deben envolver sin desbordarse en 320, 390, 768, 1536 y 1920 px. Mantener filtros, orden, escena sticky, movimiento reducido, no-JS, contacto y seleccion de interes. Cambiar la leyenda global de conceptos para que no describa incorrectamente fotografias reales.

## Migracion y recuperacion

Cambios aditivos sobre la base existente. Migracion de paquetes idempotente respecto de slugs existentes. seed_demo sigue sin sobrescribir contenido y no publica nuevos productos reales. Probar migracion desde el esquema previo con productos existentes y conservar sus claves y datos. Respaldo de SQLite con su API de backup, no copia improvisada durante escrituras.

## Verificacion y aceptacion

- Staff autorizado crea, edita, oculta y publica productos y paquetes; usuarios anonimos y usuarios sin permisos no pueden hacerlo.
- Fotos validas aparecen en el sitio; archivos falsos, grandes, animados y malformados muestran errores recuperables.
- Un borrador no aparece en consultas publicas y un producto publicado conserva sus datos comerciales sin habilitar compras.
- Los conceptos existentes siguen apareciendo si no hay fotografia cargada.
- SiteContent mantiene un unico registro y escapa los textos suministrados.
- Pruebas de migracion, modelos, permisos, upload y templates; pruebas de navegador con catalogo mixto y textos largos.
- Docker valida persistencia de fotos tras recrear web y servicio HTTP de medios por Nginx. No declarar Docker verificado si el daemon no esta disponible.
- Manual breve para crear administrador, cargar contenido, hacer respaldo y restaurar en un entorno de prueba.

## Limites externos

Fotografias y catalogo definitivos, Gmail y datos legales reales permanecen pendientes del cliente. El trabajo local no supone acceso o despliegue al servidor. GitHub consultado el 13 de octubre conserva e427ac4 como punta de codex/pulido-visual.

UI UX Designer y Web Design no estan instalados en las rutas de esta sesion. Antes de cambios visuales se requiere restaurarlos o autorizacion para sustituirlos por las capacidades disponibles ui-ux-pro-max, frontend-design y web-design-guidelines. No presentar una sustitucion como uso de los plugins originales.

## Modulo 2: siguiente diseno, no parte de esta implementacion

El usuario autoriza avanzar posteriormente al e-commerce. Se prepara como subsistema separado tras verificar esta entrega: PostgreSQL, variantes y precios, pedidos y estados, carrito, acceso de compradores y Stripe en modo prueba. No se activaran cobros reales ni se modificara el servidor con esta especificacion.

Antes de su especificacion hay una decision comercial necesaria: que productos tienen precio final y pueden comprarse directamente, y cuales requieren cotizacion y aprobacion del diseno. Recomendacion inicial: compra directa solo para productos expresamente habilitados y cotizacion para trabajos a medida. No inferir disponibilidad de compra a partir de precio o stock ni inventar politicas de envio, impuestos o devoluciones.

## Estado de revision

Alcance funcional aprobado en conversacion. Esta especificacion tecnica requiere revision del usuario antes de crear el plan de implementacion, conforme a Superpowers. El Modulo 2 tendra su propia especificacion y pruebas, especialmente de idempotencia, inventario y confirmacion de pagos por webhook.
