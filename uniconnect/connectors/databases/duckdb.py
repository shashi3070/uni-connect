from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import duckdb
except ImportError:
    duckdb = None


class DuckDBConnector(SyncConnector):
    name = "duckdb"
    description = "DuckDB embedded database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._connection = None

    def connect(self) -> None:
        if duckdb is None:
            raise ImportError("duckdb is required. Install with: pip install duckdb")

        path = self.config.get("path", ":memory:")
        self._connection = duckdb.connect(path)
        self._connected = True

    def close(self) -> None:
        if self._connection:
            self._connection.close()
        self._connection = None
        self._connected = False

    def query(self, sql: str, params: Optional[Any] = None) -> list[dict[str, Any]]:
        self._ensure_connected()
        if params:
            result = self._connection.execute(sql, params)
        else:
            result = self._connection.execute(sql)
        columns = [desc[0] for desc in result.description] if result.description else []
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def execute(self, sql: str, params: Optional[Any] = None) -> None:
        self._ensure_connected()
        if params:
            self._connection.execute(sql, params)
        else:
            self._connection.execute(sql)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("databases", "duckdb", DuckDBConnector)
