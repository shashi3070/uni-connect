from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class Neo4jConnector(SyncConnector):
    name = "neo4j"
    description = "Neo4j graph database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._driver = None

    def connect(self) -> None:
        raise NotImplementedError("Neo4j connector: install 'neo4j' package")

    def close(self) -> None:
        if self._driver:
            self._driver.close()
        self._driver = None
        self._connected = False

    def query(self, cypher: str, params: Optional[dict] = None) -> list[dict[str, Any]]:
        raise NotImplementedError("Neo4j connector: install 'neo4j' package")


registry.register("databases", "neo4j", Neo4jConnector)
