import unittest
from datetime import datetime

from shortener.codes import ALPHABET, CODE_LENGTH, new_code
from shortener.storage import LinkStore


class NewCodeTest(unittest.TestCase):
    def test_code_has_expected_length_and_characters(self):
        code = new_code()
        self.assertEqual(len(code), CODE_LENGTH)
        self.assertTrue(set(code) <= set(ALPHABET))


class LinkStoreTest(unittest.TestCase):
    def setUp(self):
        self.store = LinkStore(":memory:")

    def tearDown(self):
        self.store.close()

    def test_create_then_get_returns_url_and_owner(self):
        code = self.store.create("https://example.com/a", "alice")
        link = self.store.get(code)
        self.assertEqual(link["url"], "https://example.com/a")
        self.assertEqual(link["owner"], "alice")

    def test_each_create_gets_a_new_code(self):
        a = self.store.create("https://example.com/a", "alice")
        b = self.store.create("https://example.com/a", "alice")
        self.assertNotEqual(a, b)

    def test_get_unknown_code_returns_none(self):
        self.assertIsNone(self.store.get("nope"))

    def _hours_to_expiry(self, code):
        created = self.store._conn.execute(
            "SELECT created_at FROM links WHERE code = ?", (code,)
        ).fetchone()[0]
        expires = self.store.get(code)["expires_at"]
        fmt = "%Y-%m-%d %H:%M:%S"
        delta = datetime.strptime(expires, fmt) - datetime.strptime(created, fmt)
        return delta.total_seconds() / 3600

    def test_link_created_with_3_days_expires_72_hours_after_creation(self):
        code = self.store.create("https://example.com/a", "alice", 3)
        self.assertEqual(self._hours_to_expiry(code), 72)

    def test_link_created_with_no_duration_expires_720_hours_after_creation(self):
        code = self.store.create("https://example.com/a", "alice")
        self.assertEqual(self._hours_to_expiry(code), 720)


if __name__ == "__main__":
    unittest.main()
