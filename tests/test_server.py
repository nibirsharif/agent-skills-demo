import http.client
import json
import threading
import unittest

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

    def test_redirect_to_long_url(self):
        _, payload = self.create("https://example.com/page")
        code = json.loads(payload)["code"]
        response, _ = self.request("GET", f"/{code}")
        self.assertEqual(response.status, 302)
        self.assertEqual(response.getheader("Location"), "https://example.com/page")

    def test_unknown_code_returns_404(self):
        response, _ = self.request("GET", "/missing")
        self.assertEqual(response.status, 404)


if __name__ == "__main__":
    unittest.main()
