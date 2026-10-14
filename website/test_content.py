from io import BytesIO
import tempfile

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import Product, Package, SiteContent


class ContentTests(TestCase):
    def test_new_products_and_packages_are_drafts(self):
        self.assertFalse(Product().is_active)
        self.assertFalse(Package().is_active)

    def test_admin_requires_staff(self):
        self.assertEqual(self.client.get('/admin/').status_code, 302)
        user = get_user_model().objects.create_user('visitor', password='test-password-237')
        self.client.force_login(user)
        self.assertEqual(self.client.get('/admin/').status_code, 302)
        user.is_staff = True
        user.save()
        self.assertEqual(self.client.get('/admin/website/product/').status_code, 403)

    def test_content_singleton_and_escaping(self):
        content = SiteContent.objects.create(intro_title='<script>alert(1)</script>')
        with self.assertRaises(ValidationError):
            SiteContent().full_clean()
        self.assertContains(self.client.get('/'), '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertEqual(content.pk, 1)

    def test_draft_packages_hidden(self):
        Package.objects.create(slug='draft', name='Hidden package')
        self.assertNotContains(self.client.get('/'), 'Hidden package')

    def test_upload_reencoded_and_invalid_rejected(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            data = BytesIO()
            Image.new('RGB', (40, 30), 'cyan').save(data, format='PNG')
            product = Product(name='Photo', slug='photo', sku='PHOTO', description='Photo',
                              category='regalos', technique_key='dtf', image_alt='Blue product')
            product.photo = SimpleUploadedFile('unsafe-name.png', data.getvalue(), 'image/png')
            product.save()
            self.assertTrue(product.photo.name.endswith('.webp'))
            self.assertNotIn('unsafe-name', product.photo.name)
            self.assertTrue(product.image_url.startswith('/media/'))
            product.photo = SimpleUploadedFile('fake.png', b'<html>bad</html>', 'image/png')
            with self.assertRaises(ValidationError):
                product.save()

    def test_published_photo_requires_alt(self):
        product = Product(is_active=True, photo='photos/test.webp')
        with self.assertRaises(ValidationError):
            product.clean()

    def test_staff_editor_can_edit_only_with_model_permissions(self):
        from django.contrib.auth.models import Permission
        user = get_user_model().objects.create_user('editor', password='strong-237-content', is_staff=True)
        user.user_permissions.add(*Permission.objects.filter(content_type__app_label='website', codename__in=['add_package', 'view_package', 'change_package']))
        self.client.force_login(user)
        response = self.client.post('/admin/website/package/add/', {
            'slug': 'new-package', 'name': 'A new package', 'description': 'Description',
            'inclusions': 'Two pieces', 'cta': 'Cotizar', 'interest': 'regalo',
            'icon': 'gift', 'sort_order': '0', '_save': 'Save',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Package.objects.get(slug='new-package').is_active)
        self.assertNotContains(self.client.get('/'), 'A new package')
        self.assertEqual(self.client.get('/admin/auth/user/').status_code, 403)

    def test_image_limits_and_animation(self):
        from PIL import Image
        from .images import prepare_image
        with self.assertRaises(ValidationError):
            prepare_image(SimpleUploadedFile('large.png', b'x' * (5 * 1024 * 1024 + 1)))
        output = BytesIO()
        Image.new('RGB', (10, 10), 'red').save(output, format='PNG', save_all=True,
            append_images=[Image.new('RGB', (10, 10), 'blue')], duration=100, loop=0)
        with self.assertRaises(ValidationError):
            prepare_image(SimpleUploadedFile('animated.png', output.getvalue()))
        output = BytesIO()
        Image.new('RGB', (2500, 100), 'red').save(output, format='PNG')
        result = prepare_image(SimpleUploadedFile('wide.png', output.getvalue()))
        with Image.open(result) as image:
            self.assertEqual(image.width, 2400)

    def test_palette_transparency_survives_conversion(self):
        from PIL import Image
        from .images import prepare_image
        data = BytesIO()
        Image.new('P', (8, 8), 0).save(data, format='PNG', transparency=0)
        result = prepare_image(SimpleUploadedFile('transparent.png', data.getvalue()))
        with Image.open(result) as image:
            self.assertEqual(image.convert('RGBA').getpixel((0, 0))[3], 0)

    def test_public_photo_is_not_labelled_as_concept(self):
        Product.objects.create(name='Real product', slug='real', sku='REAL', description='Real',
            category='regalos', technique_key='dtf', photo='products/real.webp',
            image_alt='Actual real product', is_active=True, is_concept=False)
        response = self.client.get('/')
        self.assertContains(response, '/media/products/real.webp')
        self.assertContains(response, 'alt="Actual real product"')
        self.assertNotContains(response, 'Regalos · Concepto')
