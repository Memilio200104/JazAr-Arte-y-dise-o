# PROYECTO: JazAr Arte y Diseño - Plataforma Web Inmersiva

## 1. Naturaleza del Negocio
- **Empresa:** JazAr Arte y Diseño.
- **Propietaria:** Jazmin Zarate (Diseñadora Gráfica).
- **Giro:** Venta de prendas, regalos y textiles personalizados utilizando sublimación, DTF, impresión 3D y personalización en general.
- **Objetivo del Sitio:** Ser una carta de presentación de alto impacto. Debe transmitir que, al ser ella diseñadora gráfica, su criterio visual y calidad la convierten en la mejor opción del mercado.

## 2. Requerimientos de UI/UX y Diseño
- **Identidad:** No se cuenta con brandbook formal, pero se debe mantener coherencia con la identidad existente en su página de Facebook. El diseño debe respirar "Diseño Gráfico" (moderno, atractivo, paletas bien contrastadas).
- **Interactividad y Animaciones:** Es un requisito innegociable. El sitio debe tener múltiples animaciones, transiciones fluidas, efectos controlados por el scroll (scroll-triggered) y alta interactividad.
- **Responsividad:** 100% adaptable a cualquier dispositivo sin perder la inmersión.
- **Inspiración y Benchmarks Visuales (Nivel de calidad esperado):**
  - Apple AirPods: https://www.apple.com/mx/airpods/
  - Noomo Agency: https://noomoagency.com/
  - Lusion: https://lusion.co/
  - Moooi: https://www.moooi.com/en
- **Referencia de la Marca Actual:**
  - Facebook JazAr: https://www.facebook.com/profile.php?id=100084852678555

## 3. Arquitectura de la Información Requerida
1. **Hero / Introducción:** Quién es Jazmin y por qué su enfoque en diseño hace la diferencia.
2. **Catálogo de Productos:** Mostrando la variedad (Sublimación, DTF, Impresión 3D, etc.).
3. **Paquetes y Promociones:** Opciones específicas para vender personalización.
4. **Proceso Creativo:** Sección que explique el flujo de trabajo (cómo se convierte una idea en un producto final).
5. **Formulario de Contacto:** Conectado a un correo de Gmail.

## 4. Stack Tecnológico Estricto (Backend e Infraestructura)
- **Framework Web:** Django (Python).
- **Contenedores:** Docker y Docker Compose.
- **Servidores y Proxy:** Nginx, Gunicorn.
- **Seguridad:** Certbot (SSL/HTTPS).
- **Restricciones:** No usar automatizadores externos (como n8n) para el contacto; usar el envío nativo de Django por SMTP hacia Gmail. Las imágenes de alta calidad se proporcionarán posteriormente durante el desarrollo.

## 5. Roadmap y Escalabilidad (Aviso para el equipo)
- **Visión a Futuro (Módulo 2):** El sitio escalará en una segunda fase a un E-commerce completo (Carrito de compras, Login/Registro de usuarios y pagos con Stripe). 
- **Directiva estricta para el Módulo 1:** NO deben programar ni diseñar la lógica transaccional, de autenticación ni de pagos en esta fase. 
- **Preparación:** 
  - **UI/UX:** Contemplen el espacio visual en la navegación para futuros accesos (icono de carrito, login) para que la interfaz escale orgánicamente.
  - **Web Design:** Diseñen los modelos de base de datos del catálogo (Django Models) pensando en que eventualmente serán transaccionales (consideren incluir campos como precio o SKU desde ahora, aunque no se puedan comprar aún).

## 6. Skills obligatorias del proyecto
- En cada sesión de trabajo se deben aplicar las cuatro capacidades: **Superpowers**, **UI UX Designer**, **Web Design** y **web-design-guidelines**. Leer sus `SKILL.md` vigentes antes de aplicar sus flujos.
- Superpowers organiza diseño, planificación, ejecución y verificación según la etapa y las autorizaciones ya dadas.
- UI UX Designer conserva el sistema visual, accesibilidad, responsividad y espacio de navegación futuro.
- Web Design implementa la experiencia y sus componentes sobre Django, respetando el stack y el alcance.
- web-design-guidelines revisa los templates, CSS y JavaScript contra sus reglas vigentes antes de cerrar cambios de interfaz; registrar resultados de la revisión.
- Catálogo preparado con precio, moneda, SKU y stock no implica venta habilitada. No crear rutas, botones activos ni lógica de carrito, login de clientes, checkout, Stripe o webhooks en el Módulo 1.
