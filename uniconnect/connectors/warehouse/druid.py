from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError


class DruidConnector(SyncConnector):
    name = "druid"
    description = "Apache Druid real-time analytics database"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        try:
            from pydruid.db import connect as druid_connect
        except ImportError:
            raise ImportError("pydruid is required. Install with: pip install pydruid")

        host = self.config.get("host", "localhost")
        port = self.config.get("port", 8888)
        path = self.config.get("path", "/druid/v2/sql")
        self._client = druid_connect(host=host, port=port, path=path)
        self._connected = True

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
        self._connected = False

    def query(self, sql: str) -> list[dict[str, Any]]:
        self._ensure_connected()
        cursor = self._client.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def execute(self, sql: str) -> int:
        self._ensure_connected()
        cursor = self._client.cursor()
        cursor.execute(sql)
        return cursor.rowcount

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("warehouse", "druid", DruidConnector)
