from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    import redshift_connector
except ImportError:
    redshift_connector = None


class RedshiftConnector(SyncConnector):
    name = "redshift"
    description = "Amazon Redshift data warehouse"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._conn = None
        self._cursor = None

    def connect(self) -> None:
        driver = self.config.get("driver", "psycopg2")
        host = self.config.get("host", "")
        port = self.config.get("port", 5439)
        database = self.config.get("database", "")
        user = self.config.get("user", "")
        password = self.config.get("password", "")

        if driver == "psycopg2":
            if psycopg2 is None:
                raise ImportError("psycopg2 is required. Install with: pip install psycopg2-binary")
            self._conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=database,
                user=user,
                password=password,
            )
        elif driver == "redshift_connector":
            if redshift_connector is None:
                raise ImportError("redshift_connector is required. Install with: pip install redshift-connector")
            self._conn = redshift_connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )
        else:
            raise ValueError(f"Unsupported driver: {driver}")

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

    def copy_from_s3(self, table: str, s3_path: str, **kwargs: Any) -> None:
        self._ensure_connected()
        iam_role = kwargs.get("iam_role", self.config.get("iam_role", ""))
        region = kwargs.get("region", self.config.get("region", ""))
        sql = f"COPY {table} FROM '{s3_path}' IAM_ROLE '{iam_role}' REGION '{region}'"
        self._cursor.execute(sql)
        self._conn.commit()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("warehouse", "redshift", RedshiftConnector)
registry.register("warehouse", "redshift", RedshiftConnector, driver="psycopg2")
registry.register("warehouse", "redshift", RedshiftConnector, driver="redshift_connector")
