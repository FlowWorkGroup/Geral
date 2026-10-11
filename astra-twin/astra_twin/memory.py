"""Memória local SQLite, com histórico por sessão."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


class MemoryStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path.expanduser()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialise()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialise(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_session_id_id "
                "ON messages(session_id, id)"
            )

    def add(self, session_id: str, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError("O papel da mensagem tem de ser 'user' ou 'assistant'.")
        if not session_id.strip():
            raise ValueError("A sessão não pode estar vazia.")
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO messages(session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )

    def recent(self, session_id: str, limit: int = 12) -> list[dict[str, str]]:
        if limit < 1:
            raise ValueError("O limite tem de ser positivo.")
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT role, content FROM (
                    SELECT id, role, content FROM messages
                    WHERE session_id = ?
                    ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
                """,
                (session_id, limit),
            ).fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in rows]

    def clear_session(self, session_id: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM messages WHERE session_id = ?", (session_id,)
            )
            return cursor.rowcount
