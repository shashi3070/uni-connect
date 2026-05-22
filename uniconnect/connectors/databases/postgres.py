from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    import asyncpg
except ImportError:
    asyncpg = None


class PostgreSQLConnector(SyncConnector):
    name = "postgres"
    description = "PostgreSQL database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._connection = None
        self._pool = None

    def connect(self) -> None:
        driver = self.config.get("driver", "psycopg2")
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 5432)
        database = self.config.get("database", "")
        user = self.config.get("user", "")
        password = self.config.get("password", "")

        if driver == "psycopg2":
            if psycopg2 is None:
                raise ImportError("psycopg2 is required. Install with: pip install psycopg2-binary")
            self._connection = psycopg2.connect(
                host=host,
                port=port,
                dbname=database,
                user=user,
                password=password,
            )
            self._connection.autocommit = True
        elif driver == "asyncpg":
            if asyncpg is None:
                raise ImportError("asyncpg is required. Install with: pip install asyncpg")
            raise RuntimeError(
                "asyncpg is an async driver. Use AsyncPostgreSQLConnector instead."
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
        driver = self.config.get("driver", "psycopg2")

        if driver == "psycopg2":
            with self._connection.cursor() as cur:
                cur.execute(sql, params)
                if cur.description:
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in cur.fetchall()]
                return []

        return []

    def execute(self, sql: str, params: Optional[Any] = None) -> int:
        self._ensure_connected()
        driver = self.config.get("driver", "psycopg2")

        if driver == "psycopg2":
            with self._connection.cursor() as cur:
                cur.execute(sql, params)
                return cur.rowcount

        return 0

    def table_exists(self, name: str) -> bool:
        self._ensure_connected()
        results = self.query(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
            (name,),
        )
        return results[0]["exists"] if results else False

    def get_tables(self) -> list[str]:
        self._ensure_connected()
        results = self.query(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        return [row["table_name"] for row in results]

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("databases", "postgres", PostgreSQLConnector)
registry.register("databases", "postgres", PostgreSQLConnector, driver="psycopg2")
registry.register("databases", "postgres", PostgreSQLConnector, driver="asyncpg")
