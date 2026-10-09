import tempfile
from smtplib import SMTPException
from unittest.mock import patch

from django.core import mail
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, override_settings
from .models import Product


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="studio@example.com",
    CONTACT_EMAIL="studio@example.com",
    CONTACT_LOCAL_MODE=True,
)
class ContactTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.settings_override = override_settings(CONTACT_CACHE_DIR=self.directory.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.data = {
            "name": "Ana & Co", "email": "ana@example.com", "interest": "regalos",
            "quantity": "2", "desired_date": "", "message": "Una pieza con color <azul>.",
            "website": "",
        }

    def test_home_has_catalog_and_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["products"]), 6)
        self.assertEqual(len(response.context["packages"]), 3)

    def test_valid_submission_uses_authorized_sender_and_reply_to(self):
        response = self.client.post("/contacto/", self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, "studio@example.com")
        self.assertEqual(mail.outbox[0].reply_to, ["ana@example.com"])
        self.assertIn("<azul>", mail.outbox[0].body)
        confirmation = self.client.get(response.url)
        self.assertEqual(confirmation.context["contact_status"], "local")

    def test_invalid_fields_do_not_send(self):
        for values in ({"email": "invalid"}, {"quantity": "0"}, {"interest": "other"},
                       {"message": "x" * 5001}, {"name": "x" * 121},
                       {"desired_date": "2000-01-01"}):
            with self.subTest(values=values):
                response = self.client.post("/contacto/", {**self.data, **values})
                self.assertEqual(response.status_code, 400)
                self.assertTrue(response.context["form"].errors)
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_smtp_preserves_values(self):
        with override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
                               EMAIL_HOST_USER="", EMAIL_HOST_PASSWORD="", CONTACT_LOCAL_MODE=False):
            response = self.client.post("/contacto/", self.data)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.context["form"]["name"].value(), "Ana & Co")
        self.assertEqual(response.context["contact_status"], "error")

    def test_smtp_failure_is_not_success(self):
        with patch("website.views.EmailMessage.send", side_effect=SMTPException("unavailable")):
            response = self.client.post("/contacto/", self.data)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.context["contact_status"], "error")

    def test_honeypot_never_sends(self):
        response = self.client.post("/contacto/", {**self.data, "website": "https://spam.test"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(CONTACT_RATE_LIMIT=2)
    def test_throttle_shared_by_clients_and_ignores_untrusted_headers(self):
        self.assertEqual(self.client.post("/contacto/", self.data).status_code, 302)
        self.assertEqual(Client().post("/contacto/", self.data).status_code, 302)
        response = Client().post("/contacto/", self.data, HTTP_X_REAL_IP="different")
        self.assertEqual(response.status_code, 429)
        self.assertEqual(len(mail.outbox), 2)

    def test_csrf_is_required(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post("/contacto/", self.data).status_code, 403)

    def test_forged_success_is_ignored(self):
        self.assertEqual(self.client.get("/?contact=sent").context["contact_status"], "")

    def test_contact_is_post_only(self):
        self.assertEqual(self.client.get("/contacto/").status_code, 405)


class ProductTests(TestCase):
    def test_demo_seed_preserves_edits_and_unknown_commercial_values(self):
        call_command("seed_demo", verbosity=0)
        product = Product.objects.first()
        self.assertIsNone(product.price)
        self.assertIsNone(product.stock)
        product.name = "Nombre editado"
        product.save()
        call_command("seed_demo", verbosity=0)
        product.refresh_from_db()
        self.assertEqual(product.name, "Nombre editado")
        self.assertEqual(Product.objects.count(), 6)

    def test_product_validates_price_stock_and_unique_sku(self):
        call_command("seed_demo", verbosity=0)
        product = Product.objects.first()
        for field, value in [("price", -1), ("stock", -1), ("sku", "sku con espacios")]:
            original = getattr(product, field)
            setattr(product, field, value)
            with self.subTest(field=field), self.assertRaises(ValidationError):
                product.full_clean()
            setattr(product, field, original)
        product.sku = Product.objects.last().sku
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_inactive_product_hidden_and_no_transaction_routes(self):
        call_command("seed_demo", verbosity=0)
        Product.objects.update(is_active=False)
        self.assertEqual(len(self.client.get("/").context["products"]), 0)
        for path in ("/cart/", "/login/", "/checkout/", "/stripe/", "/admin/"):
            self.assertEqual(self.client.get(path).status_code, 404)
