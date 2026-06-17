import sqlite3
import os
from datetime import datetime


class ScrapStorage:
    """SQLite-based storage for tracking scraped URLs and latest processed date."""

    def __init__(self, db_path="storage/scrap.db", logging=None):
        self.db_path = db_path
        self.logging = logging
        self._ensure_db()

    def _get_connection(self):
        """Return a new database connection with WAL mode for better concurrency."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _ensure_db(self):
        """Create database and tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sent_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    processed_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY NOT NULL,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

    # --- URL tracking ---

    def url_already_sent(self, url):
        """Check if a URL has already been processed."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT 1 FROM sent_urls WHERE url = ?", (url,)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def mark_url_sent(self, url):
        """Mark a URL as sent/processed."""
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO sent_urls (url) VALUES (?)", (url,)
            )
            conn.commit()
        finally:
            conn.close()

    def load_all_sent_urls(self):
        """Load all sent URLs (for cases where in-memory cache is needed)."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT url FROM sent_urls ORDER BY id DESC")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    # --- State / date tracking ---

    def save_latest_date(self, date):
        """Save the latest processed article date."""
        date_iso = date.isoformat() if isinstance(date, datetime) else str(date)
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO state (key, value) VALUES (?, ?)",
                ("latest_date", date_iso),
            )
            conn.commit()
        finally:
            conn.close()

    def load_latest_date(self):
        """Load the latest processed article date."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT value FROM state WHERE key = ?", ("latest_date",)
            )
            row = cursor.fetchone()
            if row:
                return datetime.fromisoformat(row[0])
            return None
        finally:
            conn.close()

    # --- Utility ---

    def get_stats(self):
        """Return basic statistics about processed URLs."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM sent_urls")
            count = cursor.fetchone()[0]
            return {"total_sent_urls": count}
        finally:
            conn.close()
