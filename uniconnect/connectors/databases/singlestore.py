from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class SingleStoreConnector(SyncConnector):
    name = "singlestore"
    description = "SingleStore (MemSQL) database connector"

    def connect(self) -> None:
        raise NotImplementedError("SingleStore connector: install 'pymysql' or 'mysql-connector-python' package")

    def close(self) -> None:
        pass


registry.register("databases", "singlestore", SingleStoreConnector)
