# JazAr sitio funcional: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Entregar una primera versión local navegable, responsiva e interactiva con solicitud de cotización validada en Django.

**Architecture:** Django renderiza la página y procesa el contacto sin requerir JavaScript. La interfaz mejora progresivamente con GSAP, filtros y selección de productos. El correo usa SMTP Gmail en producción y un backend local explícito para pruebas, sin envíos externos durante el desarrollo.

**Tech Stack:** Django 5.2, Gunicorn, Docker Compose, Nginx, Certbot, GSAP/ScrollTrigger, CSS y JavaScript.

**Spec:** docs/fase-1-consolidado.md, docs/fase-1-narrativa.md y docs/fase-1-uiux.md (aprobados por el usuario).

## Global Constraints

- Cinco secciones: introducción, catálogo, paquetes, proceso y contacto. Sin tienda ni pagos.
- H1 JazAr Arte y Diseño; apoyo Tu idea merece un buen diseño; CTA Cotizar mi idea.
- Cian, magenta y amarillo de la referencia; tipografía Space Grotesk/Manrope; logo original pendiente.
- Imágenes conceptuales señaladas como tales, sin atribuirlas a trabajos reales; fotografías definitivas posteriores.
- Proceso: Idea, Propuesta, Aprobación, Producción, Entrega. Sin movimiento indispensable para entender contenido.
- Base SMTP Gmail nativa; no n8n. Credenciales nunca incluidas en código ni logs.
- No commits: Git pertenece a un directorio superior ajeno al proyecto; trabajar solo en este directorio autorizado.

## Review Focus

- Correo inválido, caracteres especiales y contenido extenso: validación en servidor y escape de HTML.
- Fallo o ausencia de SMTP: no mostrar éxito falso; conservar valores y permitir reintentar.
- Solicitudes repetidas y honeypot: límite compartido entre workers y ninguna filtración de contenido por logs.
- Pantallas de 320 px, teclado y movimiento reducido: navegación/formulario operables sin solapamientos.
- CDN/JavaScript/imágenes no disponibles: contenido y formulario accesibles con mejora progresiva.

## Task 1: Contacto y datos

**Files:** crear `website/forms.py`, `website/views.py`, `website/catalog.py`, `website/tests.py`; modificar `config/settings.py`, `config/urls.py`, `Dockerfile`, Compose si se requiere cache persistente.

**Interfaces:** `GET /` renderiza `website/home.html` con `form`, `products`, `packages`, `contact_status`. `POST /contacto/` valida `name`, `email`, `interest`, `quantity`, `desired_date`, `message`, `website` (honeypot). Re-renderizar página con errores; redirección tras envío correcto. Las opciones de interés incluyen familias y paquetes por claves estables.

- [x] Escribir pruebas de validación, envío locmem, Reply-To, ausencia de configuración, fallo SMTP, abuso y CSRF.
- [x] Implementar Django Form, envío EmailMessage, limitación compartida y estados del formulario.
- [x] Ejecutar pruebas con `python manage.py test website`; comprobar settings de producción y documentación de desarrollo.

## Task 2: Interfaz y movimiento

**Files:** `templates/base.html`, `templates/website/home.html`, `templates/includes/motion.html`, `static/css/site.css`, `static/js/site.js`, `static/js/motion.js`.

**Interfaces:** consumir contexto Task 1; todos los formularios incluyen CSRF. Los botones de cotización seleccionan un interés real y navegan a contacto. Filtros accesibles por técnica, menú móvil con Escape y estados de foco. `static/images/hero-concept.webp` y `collection-concept.webp` son activos conceptuales previstos; no rutas remotas frágiles.

- [x] Construir cinco secciones con copys acordados, fotografías conceptuales, controles semánticos y formulario completo.
- [x] Aplicar tipografía local, dimensiones estables y CSS responsivo; legibilidad de textos sobre hero.
- [x] Implementar filtros, preselección, menú y mejora de contacto sin impedir POST nativo.
- [x] Implementar entradas GSAP, parallax moderado y proceso sticky; desmontar en reduced-motion/móvil.
- [x] Validar viewport móvil/escritorio, teclado, ausencia de JS y estado vacío.

## Task 3: Activos e integración

**Files:** activos locales `static/images/`, `static/fonts/`, `static/vendor/`; herramientas reproducibles de prueba cuando proceda; guía `README.md`.

- [x] Crear imágenes conceptuales para establecer composición sin presentar productos ficticios como portfolio.
- [x] Incorporar dependencias locales/versionadas y licencias necesarias; verificar recursos sin 404.
- [x] Ejecutar pruebas Django, JavaScript y Compose; iniciar servidor local en puerto disponible.
- [x] Inspeccionar capturas de escritorio y móvil e interacciones reales; corregir hallazgos.
- [x] Revisión de integración por el agente principal y entrega de URL local, pruebas y límites de SMTP/HTTPS. La revisión independiente no estuvo disponible por límite de cuota de los subagentes; se registra esta limitación.

## Registro

El usuario aprobó los documentos y pidió continuar. Se conserva la división de trabajo del equipo y se ejecuta el plan en esta sesión. Las credenciales, el dominio, los productos comerciales y las fotos finales siguen pendientes; el sitio local permitirá revisar composición e interacción sin inventar esos datos.

Actualización del usuario incorporada: Product persistente con SKU, precio decimal, moneda y stock; navegación reserva espacio para dos accesos futuros. Módulo 2 explícitamente excluido: no carrito, login de clientes ni pagos. Aplicadas las cuatro skills obligatorias y registrada su continuidad en AGENTS.md.
