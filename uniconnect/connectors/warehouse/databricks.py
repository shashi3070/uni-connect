from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    from databricks import sql as dbsql
except ImportError:
    dbsql = None

try:
    from databricks.sdk import WorkspaceClient
except ImportError:
    WorkspaceClient = None


class DatabricksConnector(SyncConnector):
    name = "databricks"
    description = "Databricks lakehouse platform"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._conn = None
        self._cursor = None
        self._client = None

    def connect(self) -> None:
        driver = self.config.get("driver", "databricks-sql-connector")
        server_hostname = self.config.get("server_hostname", "")
        http_path = self.config.get("http_path", "")
        access_token = self.config.get("access_token", "")

        if driver == "databricks-sql-connector":
            if dbsql is None:
                raise ImportError("databricks-sql-connector is required. Install with: pip install databricks-sql-connector")
            self._conn = dbsql.connect(
                server_hostname=server_hostname,
                http_path=http_path,
                access_token=access_token,
            )
            self._cursor = self._conn.cursor()
        elif driver == "databricks-sdk":
            if WorkspaceClient is None:
                raise ImportError("databricks-sdk is required. Install with: pip install databricks-sdk")
            self._client = WorkspaceClient(
                host=server_hostname,
                token=access_token,
            )
        else:
            raise ValueError(f"Unsupported driver: {driver}")

        self._connected = True

    def close(self) -> None:
        if self._cursor:
            self._cursor.close()
            self._cursor = None
        if self._conn:
            self._conn.close()
            self._conn = None
        self._client = None
        self._connected = False

    def query(self, sql: str) -> list[dict[str, Any]]:
        self._ensure_connected()
        driver = self.config.get("driver", "databricks-sql-connector")

        if driver == "databricks-sql-connector":
            self._cursor.execute(sql)
            columns = [desc[0] for desc in self._cursor.description] if self._cursor.description else []
            rows = self._cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        elif driver == "databricks-sdk":
            result = self._client.statement_execution.execute_statement(
                statement=sql,
                warehouse_id=self.config.get("warehouse_id", ""),
            )
            return result.to_dict()

        return []

    def execute(self, sql: str) -> int:
        self._ensure_connected()
        driver = self.config.get("driver", "databricks-sql-connector")

        if driver == "databricks-sql-connector":
            self._cursor.execute(sql)
            self._conn.commit()
            return self._cursor.rowcount
        elif driver == "databricks-sdk":
            self._client.statement_execution.execute_statement(
                statement=sql,
                warehouse_id=self.config.get("warehouse_id", ""),
            )
            return 0

        return 0

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("warehouse", "databricks", DatabricksConnector)
registry.register("warehouse", "databricks", DatabricksConnector, driver="databricks-sql-connector")
registry.register("warehouse", "databricks", DatabricksConnector, driver="databricks-sdk")
