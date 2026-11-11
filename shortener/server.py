"""HTTP API.

POST /links   body {"url": "https://..."}, header X-User: <owner>
              -> 201 {"code": "...", "url": "..."}
GET  /links   header X-User: <owner>
              -> 200 [{"code", "url", "expires_at", "click_count", "expired"}, ...]
GET  /<code>  -> 302 to the long URL, or 404 if the code is unknown
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone
from urllib.parse import urlparse

from shortener.storage import TIME_FORMAT


def is_valid_url(url):
    if not isinstance(url, str):
        return False
    parts = urlparse(url)
    return parts.scheme in ("http", "https") and bool(parts.netloc)


class Handler(BaseHTTPRequestHandler):
    store = None  # set by make_server

    def do_POST(self):
        if self.path != "/links":
            return self._send_json(404, {"error": "not found"})
        owner = self.headers.get("X-User", "").strip()
        if not owner:
            return self._send_json(401, {"error": "X-User header is required"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._send_json(400, {"error": "body must be JSON"})
        url = body.get("url") if isinstance(body, dict) else None
        if not is_valid_url(url):
            return self._send_json(400, {"error": "url must be an http or https URL"})
        days = body.get("expires_in_days")
        if days is not None and (
            isinstance(days, bool) or not isinstance(days, int) or days < 1
        ):
            return self._send_json(
                400, {"error": "expires_in_days must be a positive whole number"}
            )
        code = self.store.create(url, owner, days)
        self._send_json(201, {"code": code, "url": url})

    def do_GET(self):
        if self.path == "/links":
            return self._list_links()
        link = self.store.get(self.path.lstrip("/"))
        if link is None:
            return self._send_json(404, {"error": "not found"})
        now = datetime.now(timezone.utc).strftime(TIME_FORMAT)
        if link["expires_at"] <= now:
            data = b"resource is permanently deleted and will not return"
            self.send_response(410)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.store.increment_clicks(link["code"])
        self.send_response(302)
        self.send_header("Location", link["url"])
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _list_links(self):
        owner = self.headers.get("X-User", "").strip()
        if not owner:
            return self._send_json(401, {"error": "X-User header is required"})
        now = datetime.now(timezone.utc).strftime(TIME_FORMAT)
        links = self.store.list_by_owner(owner)
        for link in links:
            link["expired"] = link["expires_at"] <= now
        self._send_json(200, links)

    def _send_json(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass


def make_server(store, host="127.0.0.1", port=8000):
    """Return an HTTP server that serves links from store."""
    handler = type("BoundHandler", (Handler,), {"store": store})
    return ThreadingHTTPServer((host, port), handler)
