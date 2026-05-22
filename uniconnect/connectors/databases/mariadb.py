from __future__ import annotations

from typing import Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class MariaDBConnector(SyncConnector):
    name = "mariadb"
    description = "MariaDB database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._connection = None

    def connect(self) -> None:
        try:
            import mariadb
        except ImportError:
            raise ImportError("mariadb is required. Install with: pip install mariadb")

        host = self.config.get("host", "localhost")
        port = self.config.get("port", 3306)
        database = self.config.get("database", "")
        user = self.config.get("user", "")
        password = self.config.get("password", "")

        self._connection = mariadb.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )
        self._connected = True

    def close(self) -> None:
        if self._connection:
            self._connection.close()
        self._connection = None
        self._connected = False

    def query(self, sql: str, params: Optional[dict] = None) -> list[dict]:
        self._ensure_connected()
        with self._connection.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def execute(self, sql: str, params: Optional[dict] = None) -> int:
        self._ensure_connected()
        with self._connection.cursor() as cur:
            cur.execute(sql, params)
            self._connection.commit()
            return cur.rowcount

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("databases", "mariadb", MariaDBConnector)
