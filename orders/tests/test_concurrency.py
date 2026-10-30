from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4
from django.db import connections, OperationalError
from django.test import TransactionTestCase
from . import test_requests
from orders.models import Order, OrderCreationBucket
from orders.quotes import sign_quote
from orders.services import create_order


class ConcurrentRequestTests(TransactionTestCase):
    setUp=test_requests.RequestTests.setUp
    quote=test_requests.RequestTests.quote

    def test_duplicate_parallel_submission(self):
        token=sign_quote(self.quote()); key=uuid4(); barrier=Barrier(2)
        def worker():
            try:
                barrier.wait()
                return create_order(self.customer,token,key)[0].pk
            except OperationalError:
                return None
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:worker(),range(2)))
        # A locked SQLite request is retried by the client with the same key.
        order,_=create_order(self.customer,token,key)
        self.assertTrue(all(pk is None or pk==order.pk for pk in results))
        self.assertEqual(Order.objects.count(),1)
        self.assertEqual(OrderCreationBucket.objects.get().count,1)
