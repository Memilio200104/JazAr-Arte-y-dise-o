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
