from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import cx_Oracle
except ImportError:
    cx_Oracle = None

try:
    import oracledb
except ImportError:
    oracledb = None


class OracleConnector(SyncConnector):
    name = "oracle"
    description = "Oracle database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._connection = None

    def connect(self) -> None:
        driver = self.config.get("driver", "cx_oracle")
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 1521)
        database = self.config.get("database", "")
        user = self.config.get("user", "")
        password = self.config.get("password", "")
        service_name = self.config.get("service_name", "")
        dsn = self.config.get("dsn", "")

        if driver == "cx_oracle":
            if cx_Oracle is None:
                raise ImportError("cx_Oracle is required. Install with: pip install cx-Oracle")
            if not dsn:
                if service_name:
                    dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
                else:
                    dsn = cx_Oracle.makedsn(host, port, sid=database)
            self._connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
        elif driver == "oracledb":
            if oracledb is None:
                raise ImportError("oracledb is required. Install with: pip install oracledb")
            if not dsn:
                if service_name:
                    dsn = oracledb.makedsn(host, port, service_name=service_name)
                else:
                    dsn = oracledb.makedsn(host, port, sid=database)
            self._connection = oracledb.connect(user=user, password=password, dsn=dsn)
        else:
            raise ValueError(f"Unsupported driver: {driver}")

        self._connected = True

    def close(self) -> None:
        if self._connection:
            self._connection.close()
        self._connection = None
        self._connected = False

    def query(self, sql: str, params: Optional[Any] = None) -> list[dict[str, Any]]:
        self._ensure_connected()
        with self._connection.cursor() as cur:
            cur.execute(sql, params)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
            return []

    def execute(self, sql: str, params: Optional[Any] = None) -> int:
        self._ensure_connected()
        with self._connection.cursor() as cur:
            cur.execute(sql, params)
            self._connection.commit()
            return cur.rowcount

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("databases", "oracle", OracleConnector)
registry.register("databases", "oracle", OracleConnector, driver="cx_oracle")
registry.register("databases", "oracle", OracleConnector, driver="oracledb")
