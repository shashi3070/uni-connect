from __future__ import annotations

from uniconnect.connectors.databases.postgres import PostgreSQLConnector
from uniconnect.core.registry import registry


class YugabyteDBConnector(PostgreSQLConnector):
    name = "yugabytedb"
    description = "YugabyteDB database connector (reuses PostgreSQL driver)"


registry.register("databases", "yugabytedb", YugabyteDBConnector)
registry.register("databases", "yugabytedb", YugabyteDBConnector, driver="psycopg2")
