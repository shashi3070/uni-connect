from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import mysql.connector
except ImportError:
    mysql_connector = None

try:
    import pymysql
except ImportError:
    pymysql = None


class MySQLConnector(SyncConnector):
    name = "mysql"
    description = "MySQL database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._connection = None

    def connect(self) -> None:
        driver = self.config.get("driver", "mysql-connector-python")
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 3306)
        database = self.config.get("database", "")
        user = self.config.get("user", "")
        password = self.config.get("password", "")

        if driver == "mysql-connector-python":
            if mysql_connector is None:
                raise ImportError(
                    "mysql-connector-python is required. Install with: pip install mysql-connector-python"
                )
            self._connection = mysql_connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )
        elif driver == "pymysql":
            if pymysql is None:
                raise ImportError("pymysql is required. Install with: pip install pymysql")
            self._connection = pymysql.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )
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
        driver = self.config.get("driver", "mysql-connector-python")

        if driver == "mysql-connector-python":
            with self._connection.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        elif driver == "pymysql":
            with self._connection.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql, params)
                return cur.fetchall()

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


registry.register("databases", "mysql", MySQLConnector)
registry.register("databases", "mysql", MySQLConnector, driver="mysql-connector-python")
registry.register("databases", "mysql", MySQLConnector, driver="pymysql")
