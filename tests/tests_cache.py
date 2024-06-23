from pachca_client.api.cache import Cache
import unittest
from time import sleep


class TestCacheInit(unittest.TestCase):
    def test_init_with_invalid_ttl(self):
        with self.assertRaises(ValueError):
            Cache(ttl=0)

    def test_init_with_valid_ttl(self):
        raised = False
        try:
            Cache(ttl=10)
        except Exception:
            raised = True
        self.assertFalse(raised)


class TestCacheGet(unittest.TestCase):
    def test_not_exists(self):
        c = Cache()
        users = c.get('users')
        self.assertIsNone(users)

    def test_expired(self):
        c = Cache(ttl=2)
        c.update('users', 'A')
        users = c.get('users')
        self.assertEqual(users, 'A')
        sleep(1)
        users = c.get('users')
        self.assertEqual(users, 'A')
        sleep(2)
        users = c.get('users')
        self.assertIsNone(users)
