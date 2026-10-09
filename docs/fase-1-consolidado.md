# JazAr Arte y Diseño: primera fase

Fecha: 8 de octubre de 2026. Estado: propuesta para revisión y base técnica; el sitio público todavía no está implementado.

## Objetivo y alcance

Crear una carta de presentación inmersiva para JazAr y Jazmin Zarate, diseñadora gráfica, que convierta visitas en solicitudes de cotización de prendas, regalos y textiles personalizados. La sublimación, el DTF, la impresión 3D y otras técnicas son medios para resolver la idea del cliente; el criterio de diseño es el argumento central.

Esta entrega contiene narrativa y copies, sistema visual y storyboard de movimiento, y archivos de infraestructura con un esqueleto técnico mínimo. No incluye tienda, pagos, catálogo definitivo, fotografías finales ni formulario comercial terminado. No se publica ni se envían correos en esta fase.

## Entregables del equipo

1. [Brainstorm: narrativa, copies y proceso creativo](fase-1-narrativa.md).
2. [UI/UX Designer: referencias, paleta, tipografía y storyboard](fase-1-uiux.md).
3. [Web Design: infraestructura, librerías y operación](fase-1-infraestructura.md).

## Decisiones compartidas

- Dirección recomendada: diseño con intención. Mostrar qué aporta Jazmin mediante composición, color, selección de técnica y acabado, sin afirmar premios, resultados o superioridad que no estén documentados.
- H1: **JazAr Arte y Diseño**. La propuesta de valor y la presentación de Jazmin aparecen inmediatamente después. Acción principal: **Cotizar mi idea**.
- Recorrido: introducción y autoría, catálogo, paquetes y promociones, proceso creativo y contacto.
- La captura de Facebook proporcionada por el usuario confirma una identidad de cian eléctrico, azul con volumen, magenta y amarillo neón sobre fondo oscuro con ladrillo morado. Se conserva esa energía con acentos controlados y superficies claras para catálogo y lectura. Los valores hex de la propuesta son adaptaciones para web, no colores oficiales extraídos de un brandbook. La captura permite reconocer la marca; aún se necesita el archivo original del logo.
- Movimiento con GSAP y ScrollTrigger. Lenis queda opcional; Three.js se reserva para una escena justificada con un activo real. No se necesita WebGL para navegar o solicitar una cotización.
- Hero sin bloqueo del scroll; proceso con escena fija únicamente en escritorio y progresión vertical en móvil. El contenido conserva orden de lectura y accesibilidad con movimiento reducido o sin JavaScript.
- Las imágenes de alta calidad se incorporarán después. Se definirán encuadres y proporciones desde ahora para evitar que su incorporación altere el layout. No se presentarán imágenes ajenas como trabajos de JazAr.

## Cobertura de AGENTS.md

| Requisito | Resolución en esta fase |
| --- | --- |
| Jazmin Zarate y criterio de diseño como diferenciador | Narrativa de autoría, textos del hero y evidencia prevista de decisiones visuales |
| Prendas, regalos, textiles; sublimación, DTF, impresión 3D y personalización | Arquitectura del catálogo y criterios de selección por objetivo y técnica |
| Coherencia con Facebook, sin brandbook | Captura aportada por el usuario incorporada al sistema visual; adaptación web del cian, magenta y amarillo, con logo original pendiente |
| Apple, Noomo, Lusion, Moooi | Análisis con fuentes y límites de observación en el documento UI/UX |
| Múltiples animaciones, transiciones, scroll y alta interactividad | Storyboard por sección, parámetros, filtros, estados y adaptación móvil |
| Responsividad completa | Especificación desde 320 px, interacción táctil, reducción de movimiento y carga progresiva |
| Hero e introducción | Marca, presentación de Jazmin, propuesta de valor y CTA |
| Catálogo | Familias de producto y técnicas, filtros propuestos y detalle de piezas |
| Paquetes y promociones | Propuestas comerciales sin precios, descuentos ni urgencia inventados |
| Proceso creativo | Idea, propuesta, aprobación, producción y entrega; flujo a confirmar con Jazmin |
| Formulario conectado a Gmail | Diseño del flujo y configuración SMTP nativa; implementación y envío de prueba en fase siguiente |
| Django, Docker y Compose | Esqueleto técnico y archivos de contenedores |
| Nginx y Gunicorn | Proxy, servicio WSGI y separación de estáticos |
| Certbot y HTTPS | Configuración y secuencia de emisión, activación TLS y renovación documentadas |
| Sin n8n u otros automatizadores de contacto | Envío mediante backend SMTP de Django |
| Fotografías posteriores | Integración de activos y criterios de encuadre previstos |

## Datos necesarios antes de publicar

Se requieren archivo original del logo (la captura de Facebook ya sirve como referencia visual); fotografías autorizadas; catálogo y paquetes reales; precios o reglas de cotización; cantidades mínimas, tiempos y cobertura de entrega; confirmación del proceso de aprobación; dominio con DNS y servidor; dirección Gmail destinataria y credencial SMTP configurada fuera del repositorio. Estos datos no impiden revisar la propuesta, pero sí completar contenido y despliegue reales.

La siguiente fase podrá implementar el diseño elegido, conectar el formulario y comprobar navegación, movimiento, accesibilidad, rendimiento y correo con contenido real. Las comprobaciones técnicas de esta entrega se registran en el documento de infraestructura; la existencia de los archivos no equivale a un despliegue verificado.
