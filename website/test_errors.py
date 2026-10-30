from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.test import Client, TestCase, override_settings
from django.urls import path
from config.urls import urlpatterns as site_urls


def crash(request):
    raise RuntimeError('private-debug-secret')


def forbidden(request):
    raise PermissionDenied('private-debug-secret')


def bad_request(request):
    raise SuspiciousOperation('private-debug-secret')


urlpatterns = [path('test-crash/', crash), path('test-denied/', forbidden), path('test-bad/', bad_request)] + site_urls
handler400 = 'website.errors.bad_request'
handler403 = 'website.errors.permission_denied'
handler404 = 'website.errors.page_not_found'
handler500 = 'website.errors.server_error'


@override_settings(DEBUG=False, ROOT_URLCONF=__name__)
class ErrorPageTests(TestCase):
    def test_error_handlers_render_without_database_or_exception_details(self):
        client = Client(raise_request_exception=False)
        for path, status in [('/missing-art/',404),('/test-crash/',500),('/test-denied/',403),('/test-bad/',400)]:
            with self.subTest(status=status), self.assertNumQueries(0):
                response = client.get(path)
                self.assertEqual(response.status_code, status)
                self.assertContains(response, 'Volver al inicio', status_code=status)
                self.assertContains(response, 'JazAr', status_code=status)
                self.assertNotContains(response, 'private-debug-secret', status_code=status)

    def test_csrf_failure_uses_art_page(self):
        response = Client(enforce_csrf_checks=True).post('/contacto/', {})
        self.assertContains(response, 'Volver al inicio', status_code=403)

    def test_home_has_favicon(self):
        self.assertContains(self.client.get('/'), 'icons/favicon.ico')


class ErrorPreviewTests(TestCase):
    @override_settings(DEBUG=True)
    def test_local_previews_reuse_art_pages(self):
        from .errors import MESSAGES
        for status, (title, _) in MESSAGES.items():
            with self.subTest(status=status), self.assertNumQueries(0):
                response = self.client.get(f'/tienda/revision/errores/{status}/')
                self.assertContains(response, title, status_code=status)
                self.assertIn('no-store', response.headers['Cache-Control'])

    @override_settings(DEBUG=False)
    def test_previews_are_hidden_in_production(self):
        for status in [400, 403, 404, 500]:
            response = self.client.get(f'/tienda/revision/errores/{status}/')
            self.assertEqual(response.status_code, 404)
            self.assertNotIn('no-store', response.headers.get('Cache-Control', ''))

    @override_settings(DEBUG=True)
    def test_unknown_code_and_post_not_supported(self):
        self.assertEqual(self.client.get('/tienda/revision/errores/418/').status_code, 404)
        self.assertEqual(self.client.post('/tienda/revision/errores/500/').status_code, 405)
