# Módulo 1: estado de la demo

9 de octubre de 2026. Amplía los documentos de primera fase aprobados; no los sustituye como registro de la propuesta.

## Implementado

Proyecto Django `config` y aplicación `website`, carga automática de `.env`, SQLite migrada y catálogo en el modelo Product. Página con las cinco secciones, filtros por técnica, enlaces a cotización, paquetes desplegables, proceso con indicador de avance, entradas y parallax con GSAP, menú móvil, y formulario con envío local verificable y backend SMTP preparado.

Se conserva scroll nativo; Lenis y Three.js no son necesarios para esta demo. No hay modelo 3D real para justificar WebGL. El proceso actual ilustra cinco etapas sobre una composición conceptual; las fotografías reales del trabajo permitirán completar la transformación visual de cada etapa. Logo original, fotografías, precios, paquetes definitivos, dominio y Gmail siguen pendientes.

## Roadmap incorporado

- `Product`: name, slug, sku único, description, category, technique_key, image, price decimal, currency, stock, is_active, is_concept, sort_order, created_at y updated_at.
- Precio e inventario desconocidos se representan con null. No se exponen precios inventados ni disponibilidad falsa.
- Navegación con espacio reservado de 88 px en escritorio y móvil para dos futuros controles de 44 px. No hay iconos deshabilitados ni acciones de compra ahora.
- Módulo 2 queda fuera: ningún carrito, login/registro de clientes, checkout, dependencia Stripe o webhook. Las tablas estándar de Django no implican un flujo de autenticación implementado.

## Skills aplicadas

Superpowers para plan, pruebas y verificación; UI UX Designer para el sistema aprobado y adaptación; Web Design para templates/CSS/JS; web-design-guidelines para revisión de interfaz. Su uso continuo quedó registrado en AGENTS.md por solicitud del usuario.

## Verificación inicial

- 13 pruebas Django pasan: validación, envío local, Reply-To, fallo SMTP, configuración incompleta, CSRF, honeypot, límite compartido, confirmación firmada, catálogo, SKU, valores comerciales e inexistencia de rutas transaccionales.
- Playwright: recursos cargan; filtros y preselección funcionan; no se detectó desbordamiento horizontal en cinco anchos; menú y Escape funcionan; formulario muestra confirmación local; contenido y formulario presentes sin JavaScript.
- Capturas revisadas en escritorio y móvil. La demo no constituye una auditoría integral de accesibilidad ni una medición real de Core Web Vitals.
- Docker/HTTPS/Gmail real pendientes de motor Docker, dominio y credenciales; no se afirma que estén desplegados.
- Compose validado con el `.env` local, sin mostrar sus valores; `makemigrations --check --dry-run` no detecta cambios pendientes.
- Los agentes delegados agotaron su cuota durante la implementación. La integración, revisión de código y pruebas se completaron en el agente principal; no se presenta como una revisión independiente adicional.

## Web Design Guidelines

Fuente consultada: https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md

Hallazgos resueltos: menú accesible sin JavaScript, estado de filtros en URL, preload de tipografía crítica, correo sin spellcheck, foco en primer campo inválido, aviso al salir con cambios de formulario y dimensiones explícitas en imágenes. Se mantiene la redacción en español y el tono de Jazmin aprobados, por encima de preferencias editoriales genéricas de las guidelines.
