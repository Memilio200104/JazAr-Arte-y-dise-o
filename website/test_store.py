from django.test import TestCase, override_settings
from .models import Product


class StoreTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Taza <arte>", slug="taza-arte", sku="TEST-STORE",
            description="Tu idea", category="regalos", technique_key="sublimacion",
            price="199.90", sale_mode="fixed", is_active=True, is_concept=False,
        )

    def test_fixed_product_detail(self):
        response = self.client.get("/productos/taza-arte/")
        self.assertContains(response, "Taza &lt;arte&gt;")
        self.assertContains(response, "MXN")
        self.assertContains(response, "data-add-product")

    def test_ineligible_detail_404(self):
        for field, value in [("is_active", False), ("is_concept", True),
                             ("sale_mode", "quote"), ("price", None)]:
            original = getattr(self.product, field)
            Product.objects.filter(pk=self.product.pk).update(**{field: value})
            self.assertEqual(self.client.get("/productos/taza-arte/").status_code, 404)
            Product.objects.filter(pk=self.product.pk).update(**{field: original})

    def test_catalog_links(self):
        self.assertContains(self.client.get("/"), "/productos/taza-arte/")
        Product.objects.filter(pk=self.product.pk).update(sale_mode="quote")
        self.assertNotContains(self.client.get("/"), "/productos/taza-arte/")

    def test_store_pages_are_get_only(self):
        from django.contrib.auth import get_user_model
        count = get_user_model().objects.count()
        for path in ["/carrito/", "/pedido/pago/"]:
            self.assertEqual(self.client.get(path).status_code, 200, path)
            self.assertEqual(self.client.post(path, {"password": "never-store"}).status_code, 405)
        self.assertEqual(get_user_model().objects.count(), count)

    @override_settings(DEBUG=False)
    def test_review_hidden_in_production(self):
        self.assertEqual(self.client.get("/tienda/revision/").status_code, 404)

    @override_settings(DEBUG=True)
    def test_review_available_locally(self):
        self.assertContains(self.client.get("/tienda/revision/"), "Ejemplos")

    def test_payment_has_no_card_fields(self):
        response = self.client.get("/pedido/pago/")
        self.assertNotContains(response, 'autocomplete="cc-number"')
        self.assertContains(response, "disabled")

    @override_settings(CONTACT_LOCAL_MODE=True)
    def test_public_copy(self):
        response = self.client.get("/")
        self.assertNotContains(response, "Demo local")
        self.assertContains(response, "hero-concept.webp")
        self.assertContains(response, "correo")
