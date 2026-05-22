from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class CouchbaseConnector(SyncConnector):
    name = "couchbase"
    description = "Couchbase database connector"

    def connect(self) -> None:
        raise NotImplementedError("Couchbase connector: install 'couchbase' package")

    def close(self) -> None:
        pass


registry.register("databases", "couchbase", CouchbaseConnector)
