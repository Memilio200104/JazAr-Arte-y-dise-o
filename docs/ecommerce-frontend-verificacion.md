# Frontend e-commerce: verificacion local

20 de octubre de 2026. No implica backend transaccional terminado ni despliegue.

## Entregado

Ficha por producto fijo, carrito persistido en navegador, acceso/registro/recuperacion, cuenta sin sesion, composicion de solicitud y pago pendiente de aprobacion. Las acciones transaccionales estan deshabilitadas. Revision de estados en `/tienda/revision/`, solamente DEBUG=True.

Portada conserva hero-concept.webp por correccion expresa del usuario. Se retiro la etiqueta publica de demo; el contacto informa que Gmail aun no esta disponible.

## Evidencia

- 40 pruebas Django pasan, incluidas rutas GET-only, elegibilidad, escape de HTML y aislamiento de revision en produccion.
- Node: normalizacion de cantidades, precio autoritativo del catalogo, cero stock, identificadores invalidos, duplicados y aviso al alcanzar limite.
- Playwright check_store: 320, 390, 768, 844, 1024, 1440 y 1920 px; 844 con altura 600; zoom CSS 200%; dialogo/Escape/retorno de foco; seleccion persistida, eliminar, vacio, storage corrupto o bloqueado y sin JavaScript.
- check_browser, check_client_catalog, check_process y check_hero pasan. Las pruebas antiguas de contacto se actualizaron para usar articulos cotizados y el aviso vigente.
- No hay migraciones pendientes. Los datos de inventario no se modificaron.
- Capturas locales en artifacts/store-*.png, excluidas de Git. Inspeccion visual de producto desktop y 320 px, ingreso 390 px y carrito desktop.
- Revision independiente: corregido aviso de agregado falso cuando ya se habia alcanzado la cantidad maxima; prueba RED y GREEN registrada en esta sesion.

## UI y accesibilidad

Aplicadas ui-ux-pro-max y Web Interface Guidelines obtenidas de https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md durante la revision.

- `templates/store/product_detail.html`: dialogo nativo, botones etiquetados, alt y dimensiones; foco vuelve al disparador.
- `static/css/store.css`: reduced-motion, foco visible, cifras tabulares, controles tactiles, wrapping y contencion del dialogo. Corregido espacio superior duplicado por encabezado sticky.
- `static/js/store.js`: DOM con textContent para nombres; datos publicos mediante json_script; no se persisten credenciales o direccion.
- `templates/store/screen.html`: excepcion deliberada a formularios habilitados: envio desactivado porque autenticacion/pedidos no existen. Sin atributos name en los campos para evitar serializarlos con navegacion nativa mientras no hay backend.

## Limites y seguimiento

No se ha probado un transporte, una cuenta real, un pedido real ni Stripe. No se afirma cumplimiento exhaustivo WCAG. La eliminacion de seleccion es inmediata (se puede volver a agregar desde el catalogo); considerar deshacer como mejora posterior. Las fotos conservan la resolucion del catalogo original. La revision de errores 400/403/404/500 esta cubierta por la suite Django; el script visual de errores no se repitio en esta entrega.
