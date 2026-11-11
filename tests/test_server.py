import http.client
import json
import threading
import unittest
from datetime import datetime

from shortener.server import make_server
from shortener.storage import LinkStore


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.store = LinkStore(":memory:")
        self.server = make_server(self.store, port=0)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.store.close()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        data = json.dumps(body) if body is not None else None
        conn.request(method, path, body=data, headers=headers or {})
        response = conn.getresponse()
        payload = response.read()
        conn.close()
        return response, payload

    def create(self, url, owner="alice"):
        return self.request("POST", "/links", {"url": url}, {"X-User": owner})

    def test_create_returns_code_and_records_owner(self):
        response, payload = self.create("https://example.com/page")
        self.assertEqual(response.status, 201)
        code = json.loads(payload)["code"]
        self.assertEqual(self.store.get(code)["owner"], "alice")

    def test_create_without_user_is_rejected(self):
        response, _ = self.request("POST", "/links", {"url": "https://example.com"})
        self.assertEqual(response.status, 401)

    def test_create_with_invalid_url_is_rejected(self):
        for url in ["not a url", "ftp://example.com/file", "", None]:
            with self.subTest(url=url):
                response, _ = self.create(url)
                self.assertEqual(response.status, 400)

    def test_create_with_non_json_body_is_rejected(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request("POST", "/links", body="nope", headers={"X-User": "alice"})
        self.assertEqual(conn.getresponse().status, 400)
        conn.close()

    def expiry_hours(self, code):
        created, expires = self.store._conn.execute(
            "SELECT created_at, expires_at FROM links WHERE code = ?", (code,)
        ).fetchone()
        fmt = "%Y-%m-%d %H:%M:%S"
        delta = datetime.strptime(expires, fmt) - datetime.strptime(created, fmt)
        return delta.total_seconds() / 3600

    def test_create_with_expires_in_days_expires_after_that_many_days(self):
        response, payload = self.request(
            "POST",
            "/links",
            {"url": "https://example.com", "expires_in_days": 3},
            {"X-User": "alice"},
        )
        self.assertEqual(response.status, 201)
        self.assertEqual(self.expiry_hours(json.loads(payload)["code"]), 72)

    def test_create_without_expires_in_days_expires_after_720_hours(self):
        _, payload = self.create("https://example.com")
        self.assertEqual(self.expiry_hours(json.loads(payload)["code"]), 720)

    def test_create_with_invalid_expires_in_days_is_rejected(self):
        for days in [0, -1, 1.5, "x"]:
            with self.subTest(days=days):
                response, _ = self.request(
                    "POST",
                    "/links",
                    {"url": "https://example.com", "expires_in_days": days},
                    {"X-User": "alice"},
                )
                self.assertEqual(response.status, 400)
                count = self.store._conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
                self.assertEqual(count, 0)

    def test_redirect_to_long_url(self):
        _, payload = self.create("https://example.com/page")
        code = json.loads(payload)["code"]
        response, _ = self.request("GET", f"/{code}")
        self.assertEqual(response.status, 302)
        self.assertEqual(response.getheader("Location"), "https://example.com/page")

    def test_expired_link_returns_410_and_is_not_redirected(self):
        _, payload = self.create("https://example.com/page")
        code = json.loads(payload)["code"]
        with self.store._conn:
            self.store._conn.execute(
                "UPDATE links SET expires_at = '2000-01-01 00:00:00' WHERE code = ?",
                (code,),
            )
        response, body = self.request("GET", f"/{code}")
        self.assertEqual(response.status, 410)
        self.assertIsNone(response.getheader("Location"))
        self.assertEqual(
            body.decode(), "resource is permanently deleted and will not return"
        )

    def test_redirects_are_counted_but_410_and_404_are_not(self):
        _, payload = self.create("https://example.com/page")
        code = json.loads(payload)["code"]
        self.assertEqual(self.store.get(code)["click_count"], 0)
        self.request("GET", f"/{code}")
        self.request("GET", f"/{code}")
        self.assertEqual(self.store.get(code)["click_count"], 2)
        with self.store._conn:
            self.store._conn.execute(
                "UPDATE links SET expires_at = '2000-01-01 00:00:00' WHERE code = ?",
                (code,),
            )
        response, _ = self.request("GET", f"/{code}")
        self.assertEqual(response.status, 410)
        self.assertEqual(self.store.get(code)["click_count"], 2)
        response, _ = self.request("GET", "/missing")
        self.assertEqual(response.status, 404)
        self.assertEqual(self.store.get(code)["click_count"], 2)

    def test_list_links_returns_only_the_owners_links(self):
        _, payload = self.create("https://example.com/a", "alice")
        code_a = json.loads(payload)["code"]
        self.create("https://example.com/b", "bob")
        self.request("GET", "/" + code_a)
        response, payload = self.request("GET", "/links", headers={"X-User": "alice"})
        self.assertEqual(response.status, 200)
        links = json.loads(payload)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["code"], code_a)
        self.assertEqual(links[0]["url"], "https://example.com/a")
        self.assertEqual(links[0]["click_count"], 1)
        self.assertEqual(links[0]["expires_at"], self.store.get(code_a)["expires_at"])

    def test_list_links_flags_expired_links(self):
        _, payload = self.create("https://example.com/old")
        old = json.loads(payload)["code"]
        _, payload = self.create("https://example.com/new")
        new = json.loads(payload)["code"]
        with self.store._conn:
            self.store._conn.execute(
                "UPDATE links SET expires_at = '2000-01-01 00:00:00' WHERE code = ?",
                (old,),
            )
        _, payload = self.request("GET", "/links", headers={"X-User": "alice"})
        flags = {link["code"]: link["expired"] for link in json.loads(payload)}
        self.assertEqual(flags, {old: True, new: False})

    def test_list_links_without_user_is_rejected(self):
        response, _ = self.request("GET", "/links")
        self.assertEqual(response.status, 401)

    def test_root_serves_the_html_page(self):
        response, payload = self.request("GET", "/")
        self.assertEqual(response.status, 200)
        self.assertIn("text/html", response.getheader("Content-Type"))
        self.assertIn(b"<table", payload)

    def test_unknown_code_returns_404(self):
        response, _ = self.request("GET", "/missing")
        self.assertEqual(response.status, 404)


if __name__ == "__main__":
    unittest.main()
