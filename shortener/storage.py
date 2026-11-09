"""SQLite storage for links."""

import sqlite3
import threading

from shortener.codes import new_code

SCHEMA = """
CREATE TABLE IF NOT EXISTS links (
    code TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    owner TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

MAX_ATTEMPTS = 10


class LinkStore:
    """Stores links in a SQLite database file (or ":memory:")."""

    def __init__(self, path):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        with self._lock, self._conn:
            self._conn.execute(SCHEMA)

    def create(self, url, owner):
        """Save a link and return its new short code."""
        for _ in range(MAX_ATTEMPTS):
            code = new_code()
            try:
                with self._lock, self._conn:
                    self._conn.execute(
                        "INSERT INTO links (code, url, owner) VALUES (?, ?, ?)",
                        (code, url, owner),
                    )
                return code
            except sqlite3.IntegrityError:
                continue
        raise RuntimeError("could not find a free short code")

    def get(self, code):
        """Return the link for a code as a dict, or None if unknown."""
        with self._lock:
            row = self._conn.execute(
                "SELECT code, url, owner FROM links WHERE code = ?", (code,)
            ).fetchone()
        if row is None:
            return None
        return {"code": row[0], "url": row[1], "owner": row[2]}

    def close(self):
        self._conn.close()
