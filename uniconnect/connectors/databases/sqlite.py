from __future__ import annotations

import sqlite3
from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class SQLiteConnector(SyncConnector):
    name = "sqlite"
    description = "SQLite database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._connection = None

    def connect(self) -> None:
        path = self.config.get("path", self.config.get("uri", ":memory:"))
        uri = self.config.get("uri", "")

        if uri:
            self._connection = sqlite3.connect(uri, uri=True)
        else:
            self._connection = sqlite3.connect(path)

        self._connection.row_factory = sqlite3.Row
        self._connected = True

    def close(self) -> None:
        if self._connection:
            self._connection.close()
        self._connection = None
        self._connected = False

    def query(self, sql: str, params: Optional[Any] = None) -> list[dict[str, Any]]:
        self._ensure_connected()
        with self._connection:
            cur = self._connection.execute(sql, params or ())
            columns = [desc[0] for desc in cur.description] if cur.description else []
            return [dict(zip(columns, row)) for row in cur.fetchall()]

    def execute(self, sql: str, params: Optional[Any] = None) -> int:
        self._ensure_connected()
        with self._connection:
            cur = self._connection.execute(sql, params or ())
            return cur.rowcount

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("databases", "sqlite", SQLiteConnector)
