from __future__ import annotations

from uniconnect.connectors.databases.postgres import PostgreSQLConnector
from uniconnect.core.registry import registry


class TimescaleDBConnector(PostgreSQLConnector):
    name = "timescaledb"
    description = "TimescaleDB database connector (reuses PostgreSQL driver)"


registry.register("databases", "timescaledb", TimescaleDBConnector)
registry.register("databases", "timescaledb", TimescaleDBConnector, driver="psycopg2")
