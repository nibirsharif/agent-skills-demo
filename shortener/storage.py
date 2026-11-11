"""SQLite storage for links."""

import sqlite3
import threading
from datetime import datetime, timedelta, timezone

from shortener.codes import new_code

SCHEMA = """
CREATE TABLE IF NOT EXISTS links (
    code TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    owner TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT
)
"""

MAX_ATTEMPTS = 10
DEFAULT_EXPIRY_DAYS = 30
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class LinkStore:
    """Stores links in a SQLite database file (or ":memory:")."""

    def __init__(self, path):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        with self._lock, self._conn:
            self._conn.execute(SCHEMA)
            columns = [r[1] for r in self._conn.execute("PRAGMA table_info(links)")]
            if "expires_at" not in columns:
                self._conn.execute("ALTER TABLE links ADD COLUMN expires_at TEXT")
                self._conn.execute(
                    "UPDATE links SET expires_at = "
                    "datetime(created_at, '+' || ? || ' days')",
                    (DEFAULT_EXPIRY_DAYS,),
                )

    def create(self, url, owner, expires_in_days=None):
        """Save a link and return its new short code.

        The link expires 24 hours per day of expires_in_days after creation,
        or after 30 days when none is given.
        """
        if expires_in_days is None:
            expires_in_days = DEFAULT_EXPIRY_DAYS
        created = datetime.now(timezone.utc).replace(microsecond=0)
        expires = created + timedelta(hours=24 * expires_in_days)
        for _ in range(MAX_ATTEMPTS):
            code = new_code()
            try:
                with self._lock, self._conn:
                    self._conn.execute(
                        "INSERT INTO links (code, url, owner, created_at, expires_at) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (
                            code,
                            url,
                            owner,
                            created.strftime(TIME_FORMAT),
                            expires.strftime(TIME_FORMAT),
                        ),
                    )
                return code
            except sqlite3.IntegrityError:
                continue
        raise RuntimeError("could not find a free short code")

    def get(self, code):
        """Return the link for a code as a dict, or None if unknown."""
        with self._lock:
            row = self._conn.execute(
                "SELECT code, url, owner, expires_at FROM links WHERE code = ?", (code,)
            ).fetchone()
        if row is None:
            return None
        return {"code": row[0], "url": row[1], "owner": row[2], "expires_at": row[3]}

    def close(self):
        self._conn.close()
