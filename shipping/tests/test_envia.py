import json
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, override_settings
from shipping.envia import quote_rates, ShippingUnavailable


@override_settings(ENVIA_TOKEN='fixture',ENVIA_CARRIERS=['dhl'])
class AdapterTests(SimpleTestCase):
    def test_transport_payload_and_normalization(self):
        response=MagicMock()
        response.__enter__.return_value.read.return_value=json.dumps({'data':[{
            'carrier':'dhl','service':'ground','totalPrice':'185.20','currency':'MXN'}]}).encode()
        with patch('shipping.envia.urlopen',return_value=response) as transport:
            rates=quote_rates({'country':'MX'},{'country':'MX'},[{'amount':1},{'amount':1}])
        self.assertEqual(rates[0].amount_minor,18520)
        request=transport.call_args.args[0]
        self.assertEqual(request.full_url,'https://api-test.envia.com/ship/rate/')
        self.assertEqual(request.get_header('User-agent'), 'JazAr/1.0 (+shipping integration)')
        self.assertEqual(len(json.loads(request.data)['packages']),2)

    def test_timeout_and_empty_fail_closed(self):
        with patch('shipping.envia.urlopen',side_effect=TimeoutError):
            with self.assertRaises(ShippingUnavailable): quote_rates({}, {}, [{'amount':1}])
        with override_settings(ENVIA_TOKEN=''):
            with self.assertRaises(ShippingUnavailable): quote_rates({}, {}, [{'amount':1}])
