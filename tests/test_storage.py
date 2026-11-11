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

    def test_new_link_has_0_clicks_and_two_increments_make_it_2(self):
        code = self.store.create("https://example.com/a", "alice")
        self.assertEqual(self.store.get(code)["click_count"], 0)
        self.store.increment_clicks(code)
        self.store.increment_clicks(code)
        self.assertEqual(self.store.get(code)["click_count"], 2)

    def test_list_by_owner_returns_only_that_owners_links_with_fields(self):
        a = self.store.create("https://example.com/a", "alice", 3)
        self.store.create("https://example.com/b", "bob")
        expired = self.store.create("https://example.com/c", "alice")
        self.store._conn.execute(
            "UPDATE links SET expires_at = '2000-01-01 00:00:00' WHERE code = ?",
            (expired,),
        )
        self.store.increment_clicks(a)
        links = self.store.list_by_owner("alice")
        self.assertEqual({l["code"] for l in links}, {a, expired})
        by_code = {l["code"]: l for l in links}
        self.assertEqual(by_code[a]["url"], "https://example.com/a")
        self.assertEqual(by_code[a]["click_count"], 1)
        self.assertEqual(by_code[a]["expires_at"], self.store.get(a)["expires_at"])
        self.assertEqual(by_code[expired]["expires_at"], "2000-01-01 00:00:00")
        self.assertEqual(self.store.list_by_owner("carol"), [])


if __name__ == "__main__":
    unittest.main()
