# Roadmap: panel de Jazmin y Gmail

Division acordada con el usuario el 30 de octubre de 2026. Sustituye la agrupacion anterior de ambos alcances en Modulo 3. Es una separacion de entregables, no una implementacion nueva en este cambio documental.

## Modulo 3 — Panel propio de Jazmin

Interfaz privada dentro del sitio, usable desde movil y escritorio, para que Jazmin pueda operar sin entrar habitualmente a Django admin:

- Consultar pedidos y registrar aprobacion del diseno o solicitud de cambios.
- Consultar pagos, cancelaciones y reembolsos; reutilizar las reglas del Modulo 2.
- Crear y editar productos, fotos y contenido editable; archivar productos con historial de compra.
- Modificar existencias respetando reservas y ventas registradas.
- Gestionar usuarios, incluido bloqueo de acceso con permisos administrativos.
- Registrar guias y actualizar el seguimiento manual de pedidos.

Reutilizar servicios, validaciones, permisos e historial existentes. Mantener Django admin como respaldo. El panel debe ser funcional sin Gmail configurado; los compradores no adquieren permisos administrativos.

## Modulo 3.5 — Gmail y comunicaciones por correo

- Configuracion de SMTP de Gmail mediante el envio nativo de Django, sin automatizadores externos.
- Envio real del formulario de contacto.
- Correos de verificacion y recuperacion de cuentas.
- Avisos a Jazmin de nuevos pedidos y otras alertas operativas por concretar.
- Avisos al cliente de aprobacion del diseno, cambios solicitados y cambios de estado del pedido; incluir los eventos de pago, cancelacion/reembolso y envio que correspondan.
- Plantillas de correo coherentes con JazAr y tratamiento de fallos/reintentos para no perder ni duplicar notificaciones.

Los destinatarios, textos y eventos exactos se detallaran al disenar esta fase. Las credenciales se configuran fuera de Git.

## Orden y limites

Primero completar y verificar el panel del Modulo 3; despues conectar Gmail en el Modulo 3.5. Las pruebas de cuenta pueden seguir usando el backend de correo local mientras tanto. Esta division no cambia las reglas comerciales, no activa Stripe live y no modifica el acuerdo de despliegue a cargo del usuario.

Las especificaciones y planes anteriores conservan su contexto historico. Cuando mencionen Gmail y panel juntos en Modulo 3, aplicar esta separacion y las instrucciones vigentes de AGENTS.md.

## Estimación inicial a partir del MVP

Estimación de esfuerzo, no compromiso de fecha ni tiempo de ejecución continuo del agente. Supone reutilizar los servicios actuales, mantener el alcance descrito y disponer de decisiones y credenciales cuando sean necesarias. Jornada de referencia: 8 horas productivas.

| Entrega | Diseño y definición | Implementación | Pruebas, ajustes y manual | Total aproximado |
|---|---:|---:|---:|---:|
| Módulo 3: panel de Jazmin | 8–12 h | 24–40 h | 8–12 h | **40–64 h / 5–8 jornadas** |
| Módulo 3.5: Gmail | 4–8 h | 12–20 h | 8–12 h | **24–40 h / 3–5 jornadas** |

Total secuencial: **64–104 horas / 8–13 jornadas**, aproximadamente **2–3 semanas de trabajo** con disponibilidad regular. Las esperas por revisiones, acceso a Gmail o validaciones externas se suman al calendario; no están contadas como horas de implementación.

El Módulo 3 incluye interfaz móvil/escritorio, permisos, pedidos, aprobación, catálogo, fotos, existencias, bloqueo de usuarios, guías, consulta/recuperación de pagos y devoluciones, auditoría y documentación. No incluye analítica avanzada, generación automática de etiquetas ni una nueva plataforma de roles configurables.

El Módulo 3.5 incluye SMTP nativo, plantillas, contacto, enlaces de cuenta, avisos por eventos acordados, registro de entregas/fallos, reintentos y prevención de duplicados. El volumen esperado, la cuenta emisora y el mecanismo de ejecución de reintentos se concretarán al iniciar la fase. No incluye campañas de marketing ni una bandeja de correo dentro del sitio.

La estimación se revisará después de cerrar las pantallas del panel y la lista de notificaciones. Cada módulo actualizará el [manual del MVP](manual/README.md) junto con su implementación. El despliegue y la activación de cobros reales se coordinan por separado.
