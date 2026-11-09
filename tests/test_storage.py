import unittest

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


if __name__ == "__main__":
    unittest.main()
