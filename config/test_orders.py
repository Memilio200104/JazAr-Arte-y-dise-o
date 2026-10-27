"""File-backed SQLite test database for concurrency verification only."""
from .test_accounts_browser import *
from copy import deepcopy

DATABASES = deepcopy(DATABASES)
DATABASES['default'].setdefault('TEST', {})['NAME'] = BASE_DIR / 'runtime' / 'orders-concurrency-test.sqlite3'
