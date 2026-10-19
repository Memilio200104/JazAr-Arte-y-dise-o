# Modulo 1: cierre funcional local

Actualizado el 19 de octubre de 2026.

## Implementado

- Django, catalogo editable, paquetes, portada y panel privado.
- 85 fichas: 79 con precio fijo y 6 por cotizacion. Fotografias del cliente, retrato de Jazmin y taller real.
- Filtros por tecnica, DTF sobre prendas negras y precios separados cuando cambia la variante.
- Formulario con validacion, CSRF, honeypot, limite de solicitudes y manejo de fallos; backend SMTP preparado, no activado.
- Contacto directo por WhatsApp y Facebook.
- Proceso animado desde 768px de ancho y 600px de alto; lectura compacta en pantallas mas pequenas/bajas y con movimiento reducido.
- Paginas 400, 403, 404 y 500 con identidad artistica, enlaces de recuperacion y sin detalles internos.
- Favicon derivado del logo, formatos ICO/PNG/Apple Touch.
- Cuenta local jazar_admin creada sin contrasena predeterminada. El propietario completa `python manage.py changepassword jazar_admin`.

## Decisiones del usuario

Contenido comercial aprobado. El usuario se encarga del despliegue y reporta la operacion como probada. No desplegar hasta finalizar ambos modulos. Gmail se configura al final del Modulo 2; las pruebas locales mantienen aviso explicito de que no envian correo.

Esto cierra la entrega funcional local del Modulo 1, no certifica produccion ni entrega real de correo. No hace falta crear carrito o Stripe para terminar este alcance.

## Verificacion

32 pruebas Django: incluyen handlers con DEBUG=False, codigos HTTP correctos, ausencia de detalles de excepcion, renderizado sin consultas de base de datos y rechazo CSRF personalizado. Suites de navegador para catalogo, filtros, contacto local, responsividad y proceso. No constituye auditoria integral de accesibilidad ni medicion de Core Web Vitals.

El agente no ha validado Docker, TLS o SMTP reales. Las advertencias locales de `check --deploy` no se ocultan ni se confunden con el estado de un servidor.

## Siguiente modulo

Especificar envio/recogida, variantes, captura y aprobacion del diseno, stock, cuenta/invitado, pedidos y momento del cobro. Stripe se integra inicialmente en pruebas. No hay rutas transaccionales activas.

Mejoras de lanzamiento a evaluar junto con la tienda: paginacion/busqueda del catalogo, metadatos para compartir, sitemap/robots con dominio definitivo y aviso de privacidad. El despliegue final sigue a cargo del usuario.

## Skills

Revision de cierre: ui-ux-pro-max, resultado Error Recovery (enlaces de regreso y ayuda). Web Interface Guidelines revisadas el 19 de octubre: templates de error con titulo, idioma, h1, skip link, foco visible, dimensiones de imagen y sin dependencias JavaScript. Prueba de cuatro estados en 320, 390, 844 y 1440px; capturas inspeccionadas. Los handlers conservan sus codigos HTTP, no son paginas 200 que simulan errores.

Las capturas se generan con HTML renderizado por los handlers e interceptado solo en Playwright, sin rutas publicas de fallo o de previsualizacion. La integracion HTTP real y CSRF se comprueba en Django con DEBUG=False.

Superpowers, ui-ux-pro-max y web-design-guidelines. Las menciones a los plugins antiguos en propuestas de octubre son historicas y no describen herramientas activas.
