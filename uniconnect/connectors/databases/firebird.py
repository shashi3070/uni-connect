from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class FirebirdConnector(SyncConnector):
    name = "firebird"
    description = "Firebird database connector"

    def connect(self) -> None:
        raise NotImplementedError("Firebird connector: install 'fdb' package")

    def close(self) -> None:
        pass


registry.register("databases", "firebird", FirebirdConnector)
