from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class CouchDBConnector(SyncConnector):
    name = "couchdb"
    description = "Apache CouchDB database connector"

    def connect(self) -> None:
        raise NotImplementedError("CouchDB connector: install 'couchdb' package")

    def close(self) -> None:
        pass


registry.register("databases", "couchdb", CouchDBConnector)
