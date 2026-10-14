# Contenido editable Implementation Plan

**Goal:** Editar catalogo, paquetes y portada desde Django Admin.
**Architecture:** Modelos aditivos, ImageField procesado a WebP, admin nativo y media persistente.
**Tech Stack:** Django, Pillow, SQLite, Docker, Nginx.
**Spec:** docs/superpowers/specs/2026-10-13-contenido-editable-design.md

- [x] Pruebas fallidas de borradores, permisos, fotos y portada unica en website/test_content.py.
- [x] Implementar procesamiento de imagenes, Product ampliado, Package y SiteContent; migraciones aditivas y seed de paquetes.
- [x] Configurar admin, contrasenas, rutas media y volumen Nginx; integrar templates sin modificar animaciones.
- [x] Ejecutar suite, migraciones, pruebas de navegador y revision; documentar operacion y pendientes.

## Registro

Especificacion aprobada por el usuario. Ejecucion en la rama actual para preservar su flujo runserver, sin alterar main/master. No se crean usuarios ni se habilitan cobros. Modulo 2 requiere decisiones comerciales separadas.

Resultado: 24 tests pasan. Backup SQLite previo a migraciones, cambios aditivos aplicados localmente. Suite navegador y hero pasan; textos largos verificados a 320/390/768/1536/1920. Reviewer independiente reporto transparencia indexada y clipping del CTA; pruebas fallaron antes y pasan tras corregir. Docker config valido; daemon ausente impide verificar runtime de contenedores. Manual en docs/editar-contenido.md. Skills sustitutas aprobadas y persistidas en AGENTS.md.
