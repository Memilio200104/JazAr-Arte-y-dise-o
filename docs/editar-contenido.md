# Editar el contenido de JazAr

## Inicio

Activar el entorno y ejecutar `python manage.py migrate`. En esta maquina existe `jazar_admin`, creado sin contrasena utilizable: definirla con `python manage.py changepassword jazar_admin`. En otra maquina crear su propio administrador con `python manage.py createsuperuser`. Las contrasenas se introducen de forma interactiva, nunca se guardan en Git.

Abrir http://127.0.0.1:8000/admin/ con runserver activo. Para editores, crear usuarios staff y conceder solo permisos de ver, agregar y cambiar Product, Package y SiteContent. No conceder gestion de usuarios ni superusuario a un editor habitual.

## Productos y paquetes

Los nuevos registros son borradores. Completar contenido, seleccionar tecnica/categoria, asignar SKU y subir foto. Agregar descripcion alternativa; desmarcar Concepto para fotos reales. Activar is_active para publicar. Orden menor aparece primero. El precio se muestra publicamente; precio y stock no habilitan compras. Seleccionar Precio fijo o Cotizacion explicitamente. Las impresiones 3D personalizadas requieren cotizacion; los disenos sobre prendas negras se clasifican en DTF.

Los seis conceptos anteriores se conservan ocultos. El catalogo actual se carga con `import_client_catalog`, no con `seed_demo`. Los paquetes se cargan una sola vez mediante migracion y luego se editan en el panel. Inclusiones y textos no admiten HTML.

## Portada

En Contenido de la portada agregar el unico registro o editarlo si existe. Los valores iniciales reproducen los textos anteriores. Se pueden sustituir hero y presentacion; sin fotos cargadas se conservan los activos de demostracion. Guardar cambia inmediatamente los textos publicos. No hay vista previa ni historial editorial de portada; Django Admin registra las operaciones.

## Imagenes

JPEG, PNG y WebP estaticos, maximo 5 MiB y 20 megapixeles por archivo. Se convierten a WebP, se eliminan metadatos y se limita el lado mayor a 2400 px. Los archivos son publicos: no cargar documentos confidenciales. Se conservan archivos antiguos al reemplazar fotos para permitir recuperacion.

## Respaldo y restauracion

Antes del despliegue detener escrituras editoriales. Respaldar SQLite con la API `sqlite3.Connection.backup` y copiar `runtime/media` al mismo respaldo. No copiar una base SQLite activa como si fuera un archivo estatico. En Docker, ambos viven en runtime_data; no usar `docker compose down -v` porque elimina los datos.

Para restaurar, detener web, conservar una copia del estado actual, restaurar la base y media del mismo respaldo, aplicar migraciones requeridas y levantar web. Ensayar primero en una instancia separada. Un respaldo local previo a estas migraciones se conserva en runtime/backups/before-content-20261013.sqlite3, fuera de Git; no contiene medios nuevos.

## Estado de verificacion

El estado actualizado de pruebas se registra en `docs/modulo-1-estado.md`. UI UX Pro Max aplicado a overflow y legibilidad; Web Design Guidelines revisado para labels, dimensiones de imagen, alt y foco. Esto no constituye una certificacion de accesibilidad.

El usuario reporta la operacion probada y se encarga del despliegue despues de ambos modulos. El agente no verifico Docker, SMTP Gmail, dominio o HTTPS reales. Gmail se configura al final del Modulo 2. Antes de exponer /admin/ exigir HTTPS y limitar intentos de acceso en la infraestructura; no publicar el panel con DEBUG activo.
