from datetime import timedelta
from unittest.mock import patch
from django.test import override_settings, TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from shipping.tests.test_packing import PackingTests
from shipping.envia import Rate, parse_rates, ShippingUnavailable
from shipping.services import fetch_order_rates, refresh_selected_quote

ORIGIN = dict(name='Taller', phone='5539754777', street='Aconitos', number='729',
    district='Villa', city='Coacalco', state='EM', country='MX', postalCode='55710')


@override_settings(SHIPPING_ORIGIN=ORIGIN)
class QuoteTests(TestCase):
    add = PackingTests.add
    def setUp(self):
        PackingTests.setUp(self)
        self.add(quantity=5)
        self.order.review_status = 'approved'
        self.order.shipping_address = dict(recipient='Cliente', phone='5539754777', street='Calle',
            exterior='2', interior='', district='Centro', postcode='55710', city='Coacalco', state='Estado de Mexico', reference='')
        self.order.save()

    @patch('shipping.services.quote_rates', return_value=[Rate('dhl', 'ground', 18520, 'MXN')])
    def test_snapshot_grouped_cache_and_changed_price(self, api):
        quotes = fetch_order_rates(self.customer, self.order.pk)
        self.assertEqual(quotes[0].amount_minor, 18520)
        self.assertEqual(len(quotes[0].snapshot['packages']), 2)
        self.assertLessEqual(quotes[0].expires_at, timezone.now()+timedelta(seconds=600))
        self.assertEqual(fetch_order_rates(self.customer, self.order.pk)[0].pk, quotes[0].pk)
        api.return_value = [Rate('dhl', 'ground', 19000, 'MXN')]
        fresh, changed = refresh_selected_quote(self.customer, quotes[0].pk)
        self.assertTrue(changed); self.assertEqual(fresh.amount_minor, 19000)

    @patch('shipping.services.quote_rates', return_value=[Rate('dhl', 'ground', 18520, 'MXN')])
    def test_profile_change_invalidates_and_rate_limit(self, api):
        old = fetch_order_rates(self.customer, self.order.pk)[0]
        self.box.capacity = 3; self.box.save()
        fresh, changed = refresh_selected_quote(self.customer, old.pk)
        self.assertTrue(changed)
        for _ in range(8): refresh_selected_quote(self.customer, fresh.pk)
        with self.assertRaises(ValidationError): refresh_selected_quote(self.customer, fresh.pk)

    def test_pending_rejected_before_api(self):
        self.order.review_status = 'pending'; self.order.save()
        with self.assertRaises(ValidationError): fetch_order_rates(self.customer, self.order.pk)

    def test_invalid_provider_responses(self):
        for data in ({}, {'data': 'bad'}, {'data': [{'carrier':'dhl','service':'ground','currency':'USD','totalPrice':'1'}]},
                     {'data':[{'carrier':'dhl','service':'ground','currency':'MXN','totalPrice':'NaN'}]}):
            with self.assertRaises(ShippingUnavailable): parse_rates(data)
        self.assertEqual(parse_rates({'data':[{'carrier':'dhl','service':'ground','currency':'MXN','totalPrice':'185.20'}]})[0].amount_minor,18520)
