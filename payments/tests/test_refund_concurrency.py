from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.db import close_old_connections, DatabaseError
from django.test import TransactionTestCase, override_settings
from payments.tests import test_refunds as fixtures
from payments.models import Refund
from payments.refunds import _record_request
from shipping.tests.test_quotes import ORIGIN


@override_settings(SHIPPING_ORIGIN=ORIGIN, STRIPE_SECRET_KEY='sk_test_fixture', PAYMENT_ORIGIN='http://localhost:8000')
class CancellationConcurrencyTests(TransactionTestCase):
    add = fixtures.RefundTests.add
    setUp = fixtures.RefundTests.setUp

    def test_simultaneous_cancellations_create_one_durable_request(self):
        barrier = Barrier(2)
        def submit(_):
            close_old_connections()
            barrier.wait()
            try:
                refund, created = _record_request(self.customer, self.order.pk)
                return refund.pk
            except DatabaseError:
                return None  # SQLite may ask the caller to retry after lock contention.
            finally:
                close_old_connections()
        with ThreadPoolExecutor(2) as pool:
            results = list(pool.map(submit, range(2)))
        self.assertTrue(any(results))
        self.assertEqual(Refund.objects.count(), 1)
        self.assertEqual(len({pk for pk in results if pk}), 1)
        retry, created = _record_request(self.customer, self.order.pk)
        self.assertFalse(created)
        self.assertEqual(retry.pk, Refund.objects.get().pk)
