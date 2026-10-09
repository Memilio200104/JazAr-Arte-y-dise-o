# JazAr: dirección visual y storyboard de interacción

Propuesta de primera fase. No es un diseño aprobado ni un sitio implementado. Fecha de referencia: 8 de octubre de 2026.

## 1. Objetivo y premisas

La experiencia debe convertir una idea de regalo, prenda, textil o pieza personalizada en una consulta concreta para Jazmin Zarate. El argumento diferenciador es su criterio como diseñadora gráfica: composición, color, legibilidad y elección del soporte al servicio de cada encargo. Sublimación, DTF e impresión 3D son medios para obtener el resultado, no sustitutos de esa propuesta.

Recorrido principal: identificar a JazAr y a Jazmin, explorar posibilidades, comparar paquetes, entender el proceso y solicitar una cotización. Mantener las cinco secciones del AGENTS.md y navegación directa hacia todas ellas. El formulario se envía mediante Django y SMTP a Gmail; la experiencia no depende de servicios externos de automatización.

## 2. Lectura de referencias: evidencia y límites

Se consultó el contenido público mediante extracción web. Esto permite analizar jerarquía de contenido y orientación comercial, pero no equivale a observar las animaciones en un navegador renderizado. No se midieron curvas, velocidades, transiciones ni implementaciones de estas marcas. Todos los parámetros de movimiento indicados después son una propuesta original para JazAr.

| Referente | Observado en el contenido consultado | Traducción propuesta para JazAr |
| --- | --- | --- |
| [Apple AirPods México](https://www.apple.com/mx/airpods/) | Organización por producto, imágenes descriptivas, mensajes breves de beneficio y comparación de modelos. | Producto identificable, titulares concisos y catálogo que ayude a elegir. Las fotografías deben mostrar superficie, impresión y acabado. |
| [Noomo](https://noomoagency.com/) | Posicionamiento explícito en narrativa, experiencias 3D y trabajo artesanal; servicios, evidencia de proyectos y contacto. | El recorrido debe contar cómo una intención se convierte en diseño y objeto; las decisiones de Jazmin deben ser visibles. |
| [Lusion](https://lusion.co/) | La presentación vincula diseño, movimiento, 3D y desarrollo; incluye proyectos, reel y llamadas a explorar. | Una sola transformación visual memorable, conectada con un producto real, y microinteracciones consistentes durante el resto de la visita. |
| [Moooi](https://www.moooi.com/en) | Historias de productos, colecciones por categoría y autoría de diseño en contenido destacado. | Tratar prendas y objetos como piezas diseñadas: destacar contexto, autoría y detalles sin perder acceso al catálogo. |
| [Facebook JazAr](https://www.facebook.com/profile.php?id=100084852678555) | El acceso web falló, pero la captura posterior aportada por el usuario permite observar el logo volumétrico azul/cian, líneas magenta y amarillo neón, y ladrillo púrpura oscuro. | Conservar esa identidad expresiva mediante acentos luminosos controlados, respetando el logo original. Los HEX propuestos son adaptaciones web, no valores oficiales extraídos de la captura. |

No se reutilizarán logos, fotografías, efectos identificativos ni modelos 3D de los referentes. El nivel de acabado es una aspiración; alcanzarlo requiere activos propios y pruebas sobre el sitio final.

## 3. Dirección visual: diseño con intención

Un estudio editorial vivo que conserva la energía neón de Facebook: fondos limpios, tipografía precisa, fotografía de objetos y acentos eléctricos. Predominan blanco y negro para leer e inspeccionar productos; cian, magenta y amarillo conectan con la marca. El púrpura y azul profundo se conservan dentro del logo y sus composiciones, sin dominar toda la interfaz. El ladrillo es una textura de la portada actual, no un fondo obligatorio para cada sección. Los colores no se asignarán como si sublimación, DTF e impresión 3D fueran separaciones físicas de impresión CMYK.

### Paleta inicial

| Token | Valor | Uso |
| --- | --- | --- |
| Papel | `#FAFAF8` | Fondo principal, sin estética beige o artesanal rústica. |
| Tinta | `#171717` | Texto, navegación y una banda oscura del proceso. |
| Magenta de acción | `#B51658` | Adaptación oscura del acento rosa para botones legibles con texto blanco. |
| Magenta neón | `#FF3FA4` | Acento decorativo de marca, líneas breves sobre fondo oscuro; sin texto blanco pequeño. |
| Cian eléctrico | `#16D9F3` | Acento que conecta con el logo; texto tinta si se usa como superficie. |
| Cian | `#00BED0` | Señales de técnica y detalles interactivos. Texto tinta. |
| Amarillo | `#FFE065` | Acentos pequeños y avisos destacados. Texto tinta. |
| Gris legible | `#595959` | Información secundaria sobre papel. |
| Blanco | `#FFFFFF` | Texto sobre frambuesa o tinta. |

Contrastes calculados con luminancia relativa sRGB: tinta/papel 17.15:1, blanco/frambuesa 6.52:1, tinta/cian 7.92:1, tinta/amarillo 13.75:1 y gris/papel 6.70:1. Son comprobaciones de estos pares opacos; no certifican la interfaz completa. No usar blanco sobre cian ni amarillo para texto. El texto sobre fotografía llevará una superficie de imagen deliberadamente tranquila y una capa uniforme si hace falta, sin oscurecer el objeto a inspeccionar.

### Tipografía y retícula

- Titulares: [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk), pesos 500 y 600, con personalidad de estudio gráfico. Propuesta sujeta a compatibilidad con el logo existente.
- El logotipo se conserva como activo gráfico original; estas fuentes son para la interfaz y no intentan reconstruir sus letras. Se requiere el archivo original nítido, idealmente vectorial o PNG transparente de alta resolución.
- Texto y controles: [Manrope](https://fonts.google.com/specimen/Manrope), pesos 400, 500 y 600. Fuentes WOFF2 locales con `font-display: swap`, conservar sus licencias y cobertura de español.
- Escala por puntos de quiebre, sin tamaño de fuente ligado a `vw`: hero 40/56/80 px en móvil/tableta/escritorio; H2 32/40/48 px; H3 24/28/28 px; texto 16/18/18 px; etiquetas 14/14/14 px. Interlineado de titulares 1.05-1.15 y cuerpo 1.5-1.6. `letter-spacing: 0`.
- A 320 px, H1 de 36 px si la palabra más larga no cabe; permitir saltos naturales, zoom y crecimiento del contenido. Ningún texto queda recortado por una altura rígida.
- Contenido máximo 1280 px; márgenes 20 px móvil, 32 px tableta y 64 px escritorio. Retícula 4/8/12 columnas, espacios en múltiplos de 8 px. El fondo de las secciones ocupa todo el ancho.
- Sin secciones dentro de tarjetas. Solo productos, paquetes y herramientas que requieran marco usan tarjetas, radio máximo 8 px. Bordes y cambios de superficie dominan sobre sombras.
- Iconos de Lucide para menú, cerrar, flechas y estados, con nombre accesible. Herramientas solo de icono incluyen tooltip; los comandos comerciales conservan texto explícito.

## 4. Contrato general de movimiento

GSAP y ScrollTrigger controlan secuencias y progreso. La documentación permite definir `start`, `end`, `scrub` y fijación de escenas; los siguientes valores constituyen nuestro contrato inicial, pendiente de afinación visual. [Documentación oficial de ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger/).

El porcentaje de progreso es local a cada escena, nunca porcentaje de toda la página. Las animaciones ligadas directamente al desplazamiento usan `ease: none`; las entradas temporales usan `power2.out`. No hay desplazamiento horizontal forzado, ajuste automático a secciones ni bloqueo del scroll durante introducciones.

La referencia neón se traduce en líneas de acento que se revelan con `scaleX` durante 250-350 ms, una vez por sección, y halos estáticos muy localizados en el logo. Sin parpadeos, destellos, partículas ni desenfoque de pantalla completa. Sobre productos y formulario se prioriza color fiel y lectura. Con movimiento reducido, las líneas ya aparecen completas.

La versión completa se activa a partir de 1024 px de ancho y 760 px de alto, sin preferencia de movimiento reducido. En pantallas menores se conserva el relato en flujo vertical. A 200% de zoom, la adaptación de ancho debe llevar a una composición legible.

### 4.1 Hero e introducción

**Composición:** H1 literal «JazAr Arte y Diseño». Apoyo: «Tu idea merece un buen diseño». Autoría: «Con Jazmin Zarate, diseñadora gráfica». CTA «Cotizar mi idea» y enlace «Explorar productos». Fotografía propia de una composición de producto a todo el ancho, con texto sobre un área de respiro de la imagen; no dividir el hero en dos tarjetas. La marca debe identificarse en el primer vistazo.

**Encuadre:** objetivo de altura 86 `svh` en escritorio y 82 `svh` en móvil, permitiendo altura automática cuando el contenido lo requiera. En vistas estándar, debe asomar el encabezado del catálogo. En pantallas muy bajas se reduce el espacio vertical, no se recorta texto ni se sacrifica el CTA.

**Entrada:** imagen visible desde el HTML inicial; tras inicializar JS, apoyo y CTA pueden pasar de `y:16` a `0`, opacidad de 0 a 1, durante 500 ms, escalonados 70 ms. El H1 no depende de JS para verse. Ninguna espera por precarga de todas las imágenes.

**Scroll:** `start: top top`, `end: bottom top`, `scrub:0.4`. Del 0 al 70%, la capa de fotografía viaja de `y:0` a `-32px` y escala de 1 a 1.025; el texto permanece en el flujo normal. Del 70 al 100% no se añade movimiento: el catálogo entra de forma natural. No hay pin del hero ni flotación infinita. Máscara del contenedor conserva los bordes sin cortar el producto.

**Móvil:** fotografía alternativa con encuadre vertical; sin escala ni parallax. Entrada de opacidad de 200 ms y CTA ya visible. Encabezado compacto con menú accesible de 44 px mínimo por control.

### 4.2 Catálogo de productos

**Composición:** cuatro familias centradas en necesidades: «Prendas», «Regalos», «Textiles» y «Piezas 3D», con técnica como dato secundario. Filtros «Todo», «Sublimación», «DTF», «Impresión 3D» y «Otras personalizaciones», sin implicar que cualquier técnica funciona sobre cualquier soporte. Cada pieza muestra nombre, uso, técnica confirmada y enlace para cotizar ese producto.

**Entrada:** cada fila se activa cuando su borde superior llega al 85% del viewport. `y:24` a `0`, opacidad 0 a 1, 450 ms, escalonado de 60 ms, una sola vez. La reserva de tamaño se mantiene mediante `aspect-ratio:4/5` en fotos.

**Parallax:** solo fotografías de la fila destacada: de `y:12px` a `-12px` entre `start:top bottom` y `end:bottom top`, `scrub:0.35`. Texto, filtros y enlaces no se mueven. Las fotografías se encuadran con margen suficiente para no ocultar estampado, bordes ni asas.

**Interacción:** hover o foco destaca borde en 160 ms; solo hover con puntero fino permite escala de foto de 1 a 1.025 en 240 ms. Filtrar genera transición de opacidad de 180 ms, conserva foco en el filtro y anuncia la cantidad de resultados con `aria-live`. No depender de hover para descubrir acciones. «Cotizar» preselecciona el producto en el formulario sin enviar nada todavía.

**Móvil:** una columna a 320-479 px y dos desde 480 px cuando nombres y controles quepan. Filtros que ajustan líneas, sin desbordar. Sin parallax ni inclinación de tarjetas. Estado vacío con opción «Ver todos».

### 4.3 Paquetes y promociones

**Composición:** banda clara con tres paquetes propuestos: «Un regalo con intención», «Tu equipo, con identidad» y «Tu marca, en cada detalle». Los nombres, inclusiones, cantidades y condiciones definitivas se validan con Jazmin. No mostrar descuentos ficticios, contadores, precios «desde» sin base ni disponibilidad inventada.

**Movimiento:** encabezado entra a `top 80%`, `y:16` a `0` en 400 ms. Paquetes entran con opacidad y `y:20` en 450 ms, escalonado de 80 ms. Al llegar cada paquete al centro del viewport, una línea de acento crece de `scaleX:0` a `1` en 280 ms, una vez. No hay parallax: comparar datos requiere estabilidad.

**Interacción:** «Cotiza tu regalo», «Cotiza para tu equipo» y «Cotiza para tu marca» llevan al formulario con selección editable del paquete correspondiente. Las condiciones usan un disclosure semántico con botón, `aria-expanded` y transición de opacidad de 150 ms; el contenido determina su altura. No convertir toda la tarjeta en un botón si contiene otros enlaces.

**Móvil:** paquetes apilados, condiciones y CTA visibles sin carrusel obligatorio. El toque presenta las mismas opciones que teclado y ratón.

### 4.4 Proceso creativo

**Composición:** única escena extensa del recorrido, banda de tinta con texto blanco y una composición del mismo encargo: idea, propuesta, aprobación, producción y entrega. Se mostrará un caso real autorizado cuando esté disponible. El texto explica qué aporta Jazmin y qué confirma el cliente en cada paso.

**Escritorio:** la ilustración/fotografía queda sticky bajo el encabezado; la lista de cinco pasos permanece en flujo normal. Cada paso ocupa un mínimo de `60svh`, creciendo si el texto lo necesita. Área visual de alto máximo `calc(100svh - 128px)`. No apilar cinco paneles de texto transparentes unos encima de otros. La escena visual es decorativa y puede quedar `aria-hidden`; la lista mantiene toda la explicación accesible.

**Progreso:** la escena empieza cuando el primer paso alcanza el 50% de la ventana y termina cuando el quinto llega a ese mismo punto. Asociar cinco marcadores a las posiciones reales de los pasos, recalculadas después de cargar fuentes e imágenes. Rangos iniciales 0-20%, 20-40%, 40-60%, 60-80% y 80-100%; si crece un paso, los marcadores ajustan el tiempo de su imagen. Transiciones de 250 ms o `scrub:0.4`, nunca ambos compitiendo por una misma propiedad.

| Paso | Lo que muestra la escena | Movimiento concreto |
| --- | --- | --- |
| Idea | Referencia de color y objeto base con anotación del objetivo. | Entrada de dos muestras por `y:24` a `0`; parallax máximo de 16 px entre capas. |
| Propuesta | El arte se coloca sobre el soporte y se aprecia composición/escala. | Plano del arte viaja `x:-40px` a `0`, escala 0.94 a 1. El objeto mantiene una posición estable. |
| Aprobación | Vista del diseño acordado con indicación de revisión. | Detener desplazamientos; aparece un indicador de aprobación mediante opacidad. No simular la aprobación de un pedido real. |
| Producción | Detalle de la técnica elegida para ese caso, no las tres técnicas mezcladas. | Fundido de 300 ms hacia fotografía de proceso; detalle se desplaza de `y:12px` a `-12px` dentro de su intervalo. |
| Entrega | Fotografía del objeto terminado y su detalle. | Plano abre de escala 1.04 a 1 y se estabiliza; CTA de cotización visible al final del texto. |

**Alternativa 3D futura:** solo si recibimos un modelo real optimizado del producto, Three.js puede sustituir el plano visual: giro total limitado de -12 a 18 grados en Y, cámara fija y arte sobre la geometría. Sin modelo validado, usar fotografías y planos DOM; la idea de impresión 3D no exige que toda la web sea WebGL.

**Móvil y pantallas bajas:** cinco pasos completos en vertical, cada uno con imagen y explicación. Sin sticky prolongado, parallax ni canvas automático; opacidad de 200 ms al entrar si no hay movimiento reducido. El proceso se entiende aunque el visitante no complete una animación.

### 4.5 Contacto

**Composición:** fondo papel, título «Cuéntame qué quieres crear». Nombre, correo, producto/técnica opcional, cantidad aproximada opcional, fecha deseada opcional y descripción de la idea. No exigir que el cliente conozca la técnica; opción «Necesito orientación». Fecha deseada no significa disponibilidad confirmada. Teléfono solo opcional si el negocio lo necesita.

**Movimiento:** el bloque aparece mediante opacidad y `y:12` durante 350 ms a `top 85%`; nada de parallax, desplazamientos o animaciones de etiquetas mientras se escribe. Mensajes de error se asocian al campo y se ofrece resumen enfocado tras fallo de validación. No sacudir campos.

**Estados:** reposo, foco, errores, envío en curso, éxito y fallo SMTP. Botón «Enviar mi idea», cambia a «Enviando…» sin alterar anchura y previene doble envío. Solo anunciar éxito después de respuesta del servidor; aceptar el mensaje en SMTP no garantiza llegada a bandeja de entrada. En caso de fallo, conservar los valores y permitir reintentar. Incluir aviso de privacidad correspondiente al tratamiento definido por el negocio.

**Pie:** enlace de Facebook verificado, datos de contacto confirmados y navegación por anclas. No inventar teléfono, dirección, horarios o tiempo de respuesta.

## 5. Accesibilidad, adaptación y presupuesto

`prefers-reduced-motion: reduce` desactiva parallax, scrubbing, rotaciones, escala, fijaciones de escenas y suavizado Lenis; presenta las cinco imágenes y pasos de forma estática. Las acciones mantienen feedback instantáneo de color/borde. El movimiento no transmite información única. La recomendación corresponde a controlar animación no esencial según la [explicación de W3C sobre animación de interacciones](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html).

Orden de foco igual al visual, enlace para saltar al contenido, navegación con teclado, foco de alto contraste, objetivos táctiles de al menos 44 px y texto alternativo sobre lo relevante del producto. Menú móvil gestiona foco, cierre con Escape y devolución del foco. Los anclajes descuentan el encabezado mediante `scroll-margin-top`. No reemplazar cursor nativo, ni secuestrar rueda, flechas o gestos de navegación.

Todo contenido esencial y el formulario permanecen utilizables sin JavaScript. Ningún elemento se oculta permanentemente por CSS esperando que GSAP lo revele. Inicializar movimiento después de verificar dependencias; desmontarlo al cambiar preferencias o condiciones responsivas.

Presupuestos propuestos, no mediciones: imagen LCP móvil <=250 KB en AVIF/WebP cuando la calidad lo permita; JS inicial comprimido <=150 KB; ninguna dependencia Three.js o modelo 3D en la carga inicial. Meta de LCP <=2.5 s, INP <=200 ms y CLS <=0.1 a validar con pruebas y datos reales. Reservar dimensiones de imágenes; solo la imagen hero tiene prioridad alta, las demás se cargan de forma diferida.

Animar prioritariamente `transform` y `opacity`, sin blur de pantalla completa. Pausar canvas fuera de viewport y con pestaña oculta; limitar DPR a 1.5 en escritorio y 1 en móvil cuando proceda. Evitar trabajo por cada evento scroll fuera del ciclo de GSAP. Lenis es una mejora opcional de escritorio, no requisito para ninguna escena, y debe compartir un único ciclo de actualización.

## 6. Activos pendientes y validación de próxima fase

Material a incorporar: archivo original del logo (la captura de Facebook ya fue proporcionada y revisada), una composición hero horizontal y otra vertical, 6-9 fotografías de productos con técnica confirmada, un caso completo del proceso, retrato autorizado de Jazmin y detalle de acabados. Fotografías nítidas, color fiel y encuadre que permita inspeccionar el objeto. Un render provisional se identificará internamente como concepto y no se presentará como trabajo realizado.

Mientras llegan las imágenes de alta calidad, el desarrollo posterior puede usar activos temporales identificados y reemplazables, manteniendo proporciones y `alt` correctos. Esta fase solo especifica las necesidades; no crea fotografías ficticias ni un catálogo final.

La siguiente validación visual debe cubrir 320, 390, 768, 1024 y 1440 px, orientación horizontal, zoom 200%, teclado, movimiento reducido, imágenes fallidas y JavaScript desactivado. Verificar hero/CTA visibles, ausencia de solapamientos, técnica legible en cada producto, foco tras filtros, navegación por anclas y estados reales del formulario. Si se activa Three.js, añadir capturas y comprobación de píxeles del canvas para confirmar que no está vacío y que el objeto permanece completo durante su movimiento.
