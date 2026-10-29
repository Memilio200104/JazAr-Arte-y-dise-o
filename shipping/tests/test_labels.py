from django.test import SimpleTestCase
from shipping.models import ShippingQuote


class ShippingLabelTests(SimpleTestCase):
    def test_customer_labels_preserve_provider_codes(self):
        for code, label in [('ground', 'Terrestre'), ('ground_od', 'Terrestre · OD'),
                            ('express', 'Exprés'), ('local', 'Local')]:
            quote = ShippingQuote(service=code)
            self.assertEqual(quote.service_label, label)
            self.assertEqual(quote.service, code)
        self.assertEqual(ShippingQuote(service='special_service').service_label, 'special service')
