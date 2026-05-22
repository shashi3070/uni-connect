from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError


class ImpalaConnector(SyncConnector):
    name = "impala"
    description = "Apache Impala distributed SQL query engine"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._conn = None
        self._cursor = None

    def connect(self) -> None:
        try:
            from impala.dbapi import connect as impala_connect
        except ImportError:
            raise ImportError("impyla is required. Install with: pip install impyla")

        host = self.config.get("host", "localhost")
        port = self.config.get("port", 21050)
        user = self.config.get("user", "")
        database = self.config.get("database", "default")
        auth_mechanism = self.config.get("auth_mechanism", "PLAIN")

        self._conn = impala_connect(
            host=host,
            port=port,
            user=user,
            database=database,
            auth_mechanism=auth_mechanism,
        )
        self._cursor = self._conn.cursor()
        self._connected = True

    def close(self) -> None:
        if self._cursor:
            self._cursor.close()
            self._cursor = None
        if self._conn:
            self._conn.close()
            self._conn = None
        self._connected = False

    def query(self, sql: str) -> list[dict[str, Any]]:
        self._ensure_connected()
        self._cursor.execute(sql)
        columns = [desc[0] for desc in self._cursor.description] if self._cursor.description else []
        rows = self._cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def execute(self, sql: str) -> int:
        self._ensure_connected()
        self._cursor.execute(sql)
        return self._cursor.rowcount

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("warehouse", "impala", ImpalaConnector)
