from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class CassandraConnector(SyncConnector):
    name = "cassandra"
    description = "Apache Cassandra database connector"

    def connect(self) -> None:
        raise NotImplementedError("Cassandra connector: install 'cassandra-driver' package")

    def close(self) -> None:
        pass


registry.register("databases", "cassandra", CassandraConnector)
