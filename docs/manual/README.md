# Manual del MVP · JazAr Arte y Diseño

**Edición 1.0 · 30 de octubre de 2026 · Módulos 1 y 2.**

Este manual explica el uso del catálogo, las cuentas, los pedidos y la administración de JazAr. La versión funcional se integra en `main`. El entorno entregado usa Stripe y Envia en pruebas; todavía no está desplegado ni habilitado para cobrar dinero real. Gmail se conectará en el Módulo 3.5.

## Elige tu guía

| Si necesitas… | Abre… |
|---|---|
| Comprar, enviar un diseño, pagar o consultar un pedido | [Guía para compradores](cliente.md) |
| Aprobar diseños, editar productos, revisar pagos o registrar guías | [Guía de operación para Jazmin](jazmin.md) |
| Arrancar el sitio, recuperar una conexión o respaldar datos | [Anexo para el responsable técnico](operacion-tecnica.md) |
| Consultar alcance y tiempos de las próximas entregas | [Roadmap y estimaciones](../roadmap-modulos-3-y-3-5.md) |

En local, la dirección del sitio es **http://127.0.0.1:8000/**. Las rutas que aparecen en las guías se agregan a esa dirección. Cuando exista un dominio publicado, se usará ese dominio con las mismas rutas.

## Cómo funciona el MVP

**Elegir piezas → crear cuenta y dirección → solicitar revisión → enviar diseño por WhatsApp → aprobación de Jazmin → elegir envío → pagar en Stripe → consultar seguimiento.**

Los artículos de precio fijo siguen ese recorrido. Los productos señalados como cotización y las impresiones 3D personalizadas se atienden por contacto. Tener precio fijo no elimina la revisión del diseño.

La aprobación del diseño no cobra; la confirmación del pago no genera una guía. Jazmin crea la guía en Envia y registra sus datos en el administrador. Mientras Gmail esté pendiente, el cliente consulta **Mis pedidos** y la coordinación se hace por WhatsApp al **55 3975 4777**.

## Qué queda para después

- **Módulo 3:** panel propio de Jazmin dentro del sitio. Durante el MVP se utiliza Django admin.
- **Módulo 3.5:** Gmail, contacto por correo, recuperación/verificación con entrega real y avisos automáticos.
- **Activación comercial y despliegue:** a cargo del responsable del proyecto. Requiere validar empaques físicos, preparar el entorno y habilitar pagos reales explícitamente. No basta con sustituir una clave en `.env`.

## Cómo mantener este manual

Los archivos Markdown de esta carpeta son la fuente editable y se pueden leer directamente en GitHub. Cada cambio de una pantalla, botón, permiso o política debe actualizar su guía en la misma entrega de código.

1. Cambiar las instrucciones y comprobarlas contra la pantalla o implementación vigente.
2. Actualizar la edición y fecha de este índice; registrar abajo lo que cambió.
3. Revisar enlaces, rutas y ejemplos. No incluir contraseñas, claves API ni datos de compradores.
4. En el Módulo 3, sustituir los pasos cotidianos de Django admin por los del nuevo panel y conservar admin como respaldo técnico.
5. En el Módulo 3.5, documentar qué correos llegan, cuándo llegan y qué hacer si fallan. No anunciar avisos antes de implementarlos.

| Edición | Fecha | Cambio |
|---|---|---|
| 1.0 | 2026-10-30 | Primera guía del MVP: compradores, operación de Jazmin y soporte técnico. |

Las bitácoras antiguas de `docs/` conservan resultados y decisiones históricas. Para uso cotidiano, consultar este manual; para próximos módulos, el roadmap vigente.
