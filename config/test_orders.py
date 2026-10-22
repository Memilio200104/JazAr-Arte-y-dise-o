"""File-backed SQLite test database for concurrency verification only."""
from .test_accounts_browser import *

DATABASES['default']['TEST']={'NAME':BASE_DIR / 'runtime' / 'orders-concurrency-test.sqlite3'}
