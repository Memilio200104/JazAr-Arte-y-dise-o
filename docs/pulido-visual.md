# Pulido visual del Módulo 1

9 de octubre de 2026. Trabajo autorizado tras revisar la demo. Referencia estable: master, commit 2689de8. Rama de iteración: codex/pulido-visual. El repositorio ahora es propio de JazAr; el Git del directorio personal no se modifica.

## Dirección

Conservar el arte original del logo entregado por el usuario, con su cian, azul y volumen. Incorporar la identidad sin convertir cada sección en un fondo oscuro de ladrillo. El producto y la legibilidad permanecen protagonistas. Las tipografías de interfaz acompañan al logo, no lo reconstruyen.

## Esta pasada

- Incorporar originales de marca en navegación, presentación y cierre.
- Reemplazar repetición de imágenes del catálogo por conceptos específicos, manteniendo la etiqueta conceptual.
- Desarrollar cinco estados visuales para el proceso, con progreso, selección de etapa y transiciones reversibles al hacer scroll.
- Afinar entradas, hover y líneas de acento; mantener scroll nativo y versión sin movimiento.
- Verificar recursos, teclado, filtros, contacto y cinco anchos con Web Design Guidelines.

## Límites

No carrito, login de clientes, pagos ni Stripe. Origin está conectado a https://github.com/Memilio200104/JazAr-Arte-y-dise-o.git por autorización del usuario. Main y master conservan la demo 2689de8; el pulido se desarrolla por separado. No se incluye .env ni runtime en Git. GitHub respalda el código, pero no ejecuta este chat ni hospeda Django.

La demo y el pulido comparten el directorio actual para que runserver siga mostrando avances. Cambiar de rama cambia la versión que sirve ese mismo servidor; la base local ignorada se conserva. La revisión del frontend aplica Superpowers, UI UX Designer, Web Design y web-design-guidelines.

## Verificación del 9 de octubre

- 14 pruebas Django pasan. Revisión backend independiente sin bloqueadores en modelos ni contacto.
- Playwright con Chrome: recursos sin errores, filtros con URL, preselección, navegación de proceso 4-2-5 con capas asentadas, cinco anchos 320/390/768/1024/1440, menú y Escape, movimiento reducido, formulario local y contenido sin JavaScript.
- Revisión estática contra https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md: corregidos navegación sticky sin JS, controles de proceso sin JS, estado vacío de filtros y contraste de selección frente a hover. Capturas locales en artifacts, fuera de Git.
- Corregidas instrucciones que sobrescribían .env y documentada carga explícita de conceptos en la base separada de Docker.
- No verificados: entrega Gmail real, build y ejecución Docker, Nginx real, HTTPS y dispositivos físicos. No constituye certificación WCAG.

## Próximos entregables del Módulo 1

### Corrección de hero en Full HD

Corrección posterior a las capturas del usuario: el problema reportado pertenecía al proceso creativo, no al hero. El breakpoint de 760 px desactivaba la escena incluso en escritorios anchos con menor altura CSS por escalado/zoom y barras del navegador. Ahora el proceso conserva sticky desde 1024 x 600, ajusta la imagen a la altura disponible y mantiene recorrido vertical; móvil, alturas menores y movimiento reducido conservan la alternativa en flujo. Se separaron las condiciones del hero y del proceso. `scripts/check_process.cjs` falló antes a 1536 x 728 y pasa después a 1920 x 1080, 1536 x 728 y 1280 x 650; verifica etapas reversibles y que la escena completa quepa bajo el encabezado. Pruebas de hero y navegador completas también pasan.

El hero anterior solo desplazaba la imagen 32 px; no existía un recorrido fijado al scroll. Se añadió una timeline GSAP con pin bajo el encabezado y recorrido de 85% de la altura del viewport (918 px en 1920 x 1080), zoom del producto y desplazamiento de la edición. Se conserva scroll nativo, enlaces utilizables y desmontaje al activar movimiento reducido o pasar a móvil. `scripts/check_hero.cjs` reproduce el fallo previo y verifica pin y limpieza; la suite completa de navegador también pasa. Revisión Guidelines: transforms únicamente, sin interceptar rueda/teclado y con alternativa sin animación.

1. Revisar visualmente esta dirección con Jazmin y sustituir conceptos por fotos autorizadas.
2. Completar datos comerciales, condiciones de cotización y aviso de privacidad.
3. Configurar Gmail y probar recepción real antes de publicar.
4. Arrancar Docker Desktop para validar contenedores; preparar dominio, TLS y respaldo persistente al desplegar.

La hora indicada para reanudar (04:46 local) ya había pasado al continuar esta sesión. No se creó una tarea futura ni se promete ejecución con el equipo apagado. El desarrollo actual sigue siendo local.
