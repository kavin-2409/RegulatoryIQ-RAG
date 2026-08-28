import sqlite3
import json
from datetime import datetime
from loguru import logger


class VersionStore:
    """
    Stores the version history of every document we've ever downloaded.
    Uses SQLite — a simple file-based database built into Python.
    The database file lives at data/versions.db (not committed to git).
    """

    def __init__(self, db_path: str = "data/versions.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates the database file and table if they don't exist yet."""
        import os
        os.makedirs("data", exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id      TEXT NOT NULL,
                    version     INTEGER NOT NULL,
                    hash        TEXT NOT NULL,
                    content     TEXT,
                    metadata    TEXT,
                    created_at  TEXT NOT NULL
                )
            """)
            conn.commit()
        logger.info(f"VersionStore ready at {self.db_path}")

    def get_latest_hash(self, doc_id: str) -> str | None:
        """Returns the hash from the last time we downloaded this document."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT hash FROM versions WHERE doc_id = ? ORDER BY version DESC LIMIT 1",
                (doc_id,)
            ).fetchone()
        return row[0] if row else None

    def save_version(self, doc_id: str, hash: str, content: str, metadata: dict):
        """Saves a new version of a document to the database."""
        with sqlite3.connect(self.db_path) as conn:
            # Get the next version number for this document
            row = conn.execute(
                "SELECT MAX(version) FROM versions WHERE doc_id = ?", (doc_id,)
            ).fetchone()
            next_version = (row[0] or 0) + 1

            conn.execute(
                "INSERT INTO versions (doc_id, version, hash, content, metadata, created_at) VALUES (?,?,?,?,?,?)",
                (doc_id, next_version, hash, content, json.dumps(metadata), datetime.utcnow().isoformat())
            )
            conn.commit()

        logger.info(f"Saved version {next_version} of {doc_id}")

    def get_all_documents(self) -> list[dict]:
        """Returns a summary of every document we're tracking."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT doc_id, MAX(version) as latest_version, created_at
                FROM versions
                GROUP BY doc_id
                ORDER BY created_at DESC
            """).fetchall()

        return [{"doc_id": r[0], "latest_version": r[1], "last_seen": r[2]} for r in rows]
