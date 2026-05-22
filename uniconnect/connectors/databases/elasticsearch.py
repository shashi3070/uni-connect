from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class ElasticsearchConnector(SyncConnector):
    name = "elasticsearch"
    description = "Elasticsearch search and analytics engine connector"

    def connect(self) -> None:
        raise NotImplementedError("Elasticsearch connector: install 'elasticsearch' package")

    def close(self) -> None:
        pass


registry.register("databases", "elasticsearch", ElasticsearchConnector)
