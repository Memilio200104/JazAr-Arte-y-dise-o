from django.db import migrations


def seed(apps, schema_editor):
    Package = apps.get_model('website', 'Package')
    rows = [
        ('regalo', 'Un regalo con intención', 'Una pieza principal y un complemento compatible, pensados para alguien especial.', 'Cotiza tu regalo', 'gift'),
        ('equipo', 'Tu equipo, con identidad', 'Prendas con un diseño compartido y variantes de nombres cuando la técnica lo permita.', 'Cotiza para tu equipo', 'shirt'),
        ('marca', 'Tu marca, en cada detalle', 'Una propuesta para varias piezas que mantengan la misma identidad visual.', 'Cotiza para tu marca', 'layers'),
    ]
    for order, (slug, name, description, cta, icon) in enumerate(rows):
        Package.objects.using(schema_editor.connection.alias).get_or_create(slug=slug, defaults={
            'name': name, 'description': description, 'cta': cta, 'icon': icon,
            'interest': slug, 'sort_order': order, 'is_active': True,
        })


class Migration(migrations.Migration):
    dependencies = [('website', '0002_package_product_image_alt_product_photo_and_more')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
