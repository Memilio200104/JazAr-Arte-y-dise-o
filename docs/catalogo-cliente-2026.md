# Catalogo y material del cliente

## Regla comercial confirmada el 19 de octubre de 2026

- Los productos del PDF con precio fijo pertenecen a la futura venta directa, aunque sean personalizados.
- Solo se cotizan las excepciones marcadas con asteriscos y las impresiones 3D personalizadas.
- Pagina 26: caja decorada sola a $150; los articulos adicionales se cotizan. No tratar la caja sola como un paquete completo a ese precio.
- Pagina 29: servilletas, pantuflas, toallas faciales y llaveros acrilicos personalizados se cotizan por mayoreo.
- Impresion 3D: cotizar tamano, filamento, colores y detalle; no aparece en el PDF.
- Los disenos sobre prendas negras se clasifican como DTF, no sublimacion. En modelos multicolor se indica que la tecnica depende del color; no se inventan variantes de color ni inventario.
- `Product.sale_mode` es explicito, independiente de que exista `price`. Un precio de referencia nunca activa compras.
- El checkout todavia no existe. Temporalmente los productos fijos muestran su precio y permiten consultar disponibilidad; no se presenta un boton Comprar sin destino funcional.
- Pendiente del Modulo 2: especificar variantes, captura del diseno, stock, envio, impuestos y flujo Stripe en pruebas antes de habilitar ventas.

## Material integrado

Origen privado: carpeta JaZar proporcionada por el cliente. No se versiona el PDF original de 132 MB ni el DOCX.

- Catalogo completo: 85 fichas publicadas, 79 a precio fijo y 6 a cotizacion. Se incluyen todas las paginas de productos del PDF; se omiten portada y separadores de seccion. Tallas infantil/adulto, tamanos chico/grande y juegos de 4/6 tienen fichas independientes cuando cambia el precio.
- Una ficha de impresion 3D con foto real de la maquina, no una promesa de precio ni de un modelo concreto.
- Las cuatro excepciones de la pagina 29 ya tienen fotos reales y estan publicadas. La caja con articulos adicionales tiene ficha de cotizacion independiente de la caja sola de $150.
- Retrato de Jazmin, textos basados en el DOCX y cinco fotografias reales en el proceso creativo.
- La portada hero conserva su visual conceptual identificado. No se hizo pasar por una foto de producto real.
- Las fotografias compartidas entre variantes ilustran el modelo, no son una confirmacion visual de cada talla.

Las imagenes se recortaron del PDF sin regenerar ni alterar los productos. Son ejemplos visuales del catalogo, no SKU con licencia o existencias verificadas. El stock permanece desconocido.

## Reproduccion y edicion

```powershell
python manage.py migrate
python manage.py import_client_catalog --update-site --hide-demo
python manage.py runserver
```

`import_client_catalog` sin opciones es idempotente y no sobrescribe productos existentes, excepto la publicacion de los cuatro borradores iniciales de eventos si conservan nombre, descripcion e imagen de marcador originales. `--update-site` reemplaza explicitamente textos y retrato de portada. `--hide-demo` solo despublica registros conceptuales con SKU `DEMO-`; no los elimina. Editar luego en `/admin/`. No se crean usuarios ni contrasenas.

Los activos WebP estan versionados en `static/images/client`. El retrato se copia a media al importar: respaldar y servir `runtime/media` en el servidor. Antes de la carga local se guardo `runtime/backups/before-client-import-20261019.sqlite3`.

Para regenerar recortes, renderizar paginas 3-6, 8, 10-12, 14-22 y 24-31 con Poppler a 1400px de lado mayor: `pdftoppm -f 3 -l 3 -scale-to 1400 -png -singlefile <pdf> artifacts/catalog-page-3`. Ejecutar `python scripts/extract_catalog_images.py <carpeta-cliente>` con pypdf y Pillow para recuperar originales incrustados de las paginas con recortes ajustados. Luego ejecutar `node scripts/prepare_client_assets.cjs <carpeta-cliente>` con sharp disponible. Las coordenadas, correspondencias y nombres fuente estan en esos scripts. No se generan fotos sinteticas.

## Responsividad del proceso

La escena anterior se desactivaba por debajo de 1024px, incluso en paneles de escritorio con altura suficiente. CSS y GSAP ahora comparten el umbral de 768px de ancho y 600px de alto. Entre 768 y 1023px se usan dos columnas compactas y titulos de 30px. El panel fijo permanece bajo el encabezado y su imagen se limita por la altura disponible.

En pantallas mas estrechas, bajas o con movimiento reducido se conserva el flujo natural, con fotos de hasta 320px / 42svh sin recortar el producto. No se bloquea el scroll ni se fuerza una escena fija que tape el texto. Las pruebas recorren los umbrales en ambas direcciones sin recargar la pagina.

## Contacto e iconos

- WhatsApp: `https://wa.me/525539754777` (Mexico, 55 3975 4777).
- Facebook: URL editable en Contenido de la portada.
- Iconos de marca: Simple Icons, https://github.com/simple-icons/simple-icons (CC0; marcas sujetas a sus titulares). Archivos locales para evitar dependencias de red al navegar.

## Revision UI

Aplicadas las pautas de ui-ux-pro-max para iconos decorativos con texto visible, enlaces semanticos y objetivo tactil minimo de 44px.

Revision web-design-guidelines: https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md, consultada el 19 de octubre de 2026. Alcance: parciales de producto/contacto, fotografias del proceso y estilos nuevos. Iconos con alt vacio junto a nombres visibles; imagenes con dimensiones y carga diferida; precios sin indicar compra habilitada; sin nuevas animaciones automaticas. Los controles y transiciones existentes conservan reduced-motion.

Verificacion local actualizada: 29 pruebas Django aprobadas y `manage.py check` sin incidencias. `check_browser.cjs` aprobado con el catalogo completo en 320, 390, 768, 1024 y 1440px, incluyendo filtros, formulario local, recursos, teclado, reduced-motion y sin JavaScript. `check_hero.cjs` aprobado para pin/recorrido a 1920x1080 y alternativas movil/reduced-motion.

`check_process.cjs`: escena visible, contenida y reversible a 844x836, 768x700, 1023x650, 1920x1080, 1536x728 y 1280x650. Redimensionado sin recarga a 390x844, 767x800, 844x836, 844x599, 768x600 y 320x568, sin desbordamiento horizontal. Capturas inspeccionadas a 844x836 y 390x844. Esto reproduce las dimensiones del panel; no se pudo vincular directamente la pestana interna de Codex con la herramienta de navegador.

Revision web-design-guidelines renovada: estilos de proceso sin animaciones de layout, botones con etiquetas y 44px de alto, imagenes con alternativa compacta y movimiento reducido. Observacion de rendimiento para el Modulo 2: el catalogo ahora supera 50 fichas; usa imagenes WebP y carga diferida, pero conviene paginar la tienda para evitar una lista tan larga. No se declara una auditoria completa del sitio.
