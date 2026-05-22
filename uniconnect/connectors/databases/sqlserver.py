from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import pyodbc
except ImportError:
    pyodbc = None

try:
    import pymssql
except ImportError:
    pymssql = None


class SQLServerConnector(SyncConnector):
    name = "sqlserver"
    description = "Microsoft SQL Server database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._connection = None

    def connect(self) -> None:
        driver = self.config.get("driver", "pyodbc")
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 1433)
        database = self.config.get("database", "")
        user = self.config.get("user", "")
        password = self.config.get("password", "")

        if driver == "pyodbc":
            if pyodbc is None:
                raise ImportError("pyodbc is required. Install with: pip install pyodbc")
            odbc_driver = self.config.get("odbc_driver", "ODBC Driver 17 for SQL Server")
            conn_str = (
                f"DRIVER={{{odbc_driver}}};"
                f"SERVER={host},{port};"
                f"DATABASE={database};"
                f"UID={user};"
                f"PWD={password}"
            )
            self._connection = pyodbc.connect(conn_str)
        elif driver == "pymssql":
            if pymssql is None:
                raise ImportError("pymssql is required. Install with: pip install pymssql")
            self._connection = pymssql.connect(
                server=host,
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
        driver = self.config.get("driver", "pyodbc")

        if driver == "pyodbc":
            with self._connection.cursor() as cur:
                cur.execute(sql, params)
                if cur.description:
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in cur.fetchall()]
                return []
        elif driver == "pymssql":
            with self._connection.cursor(as_dict=True) as cur:
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


registry.register("databases", "sqlserver", SQLServerConnector)
registry.register("databases", "sqlserver", SQLServerConnector, driver="pyodbc")
registry.register("databases", "sqlserver", SQLServerConnector, driver="pymssql")
