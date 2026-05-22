from __future__ import annotations

from uniconnect.connectors.databases.postgres import PostgreSQLConnector
from uniconnect.core.registry import registry


class CockroachDBConnector(PostgreSQLConnector):
    name = "cockroachdb"
    description = "CockroachDB database connector (reuses PostgreSQL driver)"


registry.register("databases", "cockroachdb", CockroachDBConnector)
registry.register("databases", "cockroachdb", CockroachDBConnector, driver="psycopg2")
