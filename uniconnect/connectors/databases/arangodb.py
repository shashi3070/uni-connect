from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class ArangoDBConnector(SyncConnector):
    name = "arangodb"
    description = "ArangoDB multi-model database connector"

    def connect(self) -> None:
        raise NotImplementedError("ArangoDB connector: install 'python-arango' package")

    def close(self) -> None:
        pass


registry.register("databases", "arangodb", ArangoDBConnector)
