# Firma Quantum Qwerty

28 de octubre de 2026. Solicitud: credito discreto pero visible, tomando como referencia el pie de protegototal.com.

- Componente compartido `templates/includes/powered_by.html` en portada, tienda/cuentas/pedidos y errores publicos. No modifica Django Admin.
- Texto Powered by Quantum Qwerty y logo original copiado sin alteracion de `../Quantum-Qwerty/static/img/logo_qq.png` a `static/images/brand/quantum-qwerty.png` (10 KB).
- Tamano visual de 36 x 42 px, texto de 13 px, contraste adaptado a fondos claros/oscuros. No se invento un destino de enlace; la firma es informativa.
- Superpowers brainstorming aplicado como cambio concreto solicitado; UI UX Pro Max consultado para contraste. Revision Web Interface Guidelines: `templates/includes/powered_by.html` y `static/css/credits.css` sin hallazgos pendientes; imagen con dimensiones, carga diferida y alt vacio por nombre adyacente, sin animacion adicional ni controles sin etiqueta.
- Verificacion con navegador: portada, acceso de compradores y pagina 404 en 320/390/844/1440/1920 px; una firma por footer, logo cargado, sin overflow. Capturas de portada 1440 px y cuenta 390 px inspeccionadas. Django check y git diff --check sin errores. No cambia datos ni configuracion de proveedores.

Referencias consultadas: https://protegototal.com/ y https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md .
