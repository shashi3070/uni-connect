from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import snowflake.connector as sf_connector
except ImportError:
    sf_connector = None


class SnowflakeConnector(SyncConnector):
    name = "snowflake"
    description = "Snowflake cloud data platform"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._conn = None
        self._cursor = None

    def connect(self) -> None:
        if sf_connector is None:
            raise ImportError("snowflake-connector-python is required. Install with: pip install snowflake-connector-python")

        self._conn = sf_connector.connect(
            account=self.config.get("account", ""),
            user=self.config.get("user", ""),
            password=self.config.get("password", ""),
            warehouse=self.config.get("warehouse", ""),
            database=self.config.get("database", ""),
            schema=self.config.get("schema", "PUBLIC"),
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
        self._conn.commit()
        return self._cursor.rowcount

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("warehouse", "snowflake", SnowflakeConnector)
