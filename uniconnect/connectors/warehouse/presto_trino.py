from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError


class PrestoTrinoConnector(SyncConnector):
    name = "presto"
    description = "Presto / Trino distributed SQL query engine"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._conn = None
        self._cursor = None

    def connect(self) -> None:
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 8080)
        user = self.config.get("user", "admin")
        catalog = self.config.get("catalog", "hive")
        schema = self.config.get("schema", "default")

        try:
            import prestodb
        except ImportError:
            raise ImportError("prestodb is required. Install with: pip install presto-python-client")

        self._conn = prestodb.dbapi.connect(
            host=host,
            port=port,
            user=user,
            catalog=catalog,
            schema=schema,
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


registry.register("warehouse", "presto", PrestoTrinoConnector)
registry.register("warehouse", "trino", PrestoTrinoConnector)
