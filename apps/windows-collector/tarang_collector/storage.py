import json
from pathlib import Path
import sqlite3
from typing import Any


class OfflineQueue:
    """Resilient SQLite queue for Windows collector observations."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path), check_same_thread=False)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_observations (
                    id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def enqueue(self, obs_id: str, payload: dict[str, Any], created_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO pending_observations (id, payload_json, created_at) VALUES (?, ?, ?)",
                (obs_id, json.dumps(payload), created_at),
            )
            conn.commit()

    def pending_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM pending_observations").fetchone()
            return int(row[0]) if row else 0

    def peek_batch(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT payload_json FROM pending_observations ORDER BY created_at ASC LIMIT ?",
                (limit,),
            ).fetchall()
            return [json.loads(r[0]) for r in rows]

    def remove_ids(self, ids: list[str]) -> None:
        if not ids:
            return
        with self._connect() as conn:
            conn.executemany(
                "DELETE FROM pending_observations WHERE id = ?",
                [(i,) for i in ids],
            )
            conn.commit()
