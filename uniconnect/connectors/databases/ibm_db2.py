from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class IBMDB2Connector(SyncConnector):
    name = "ibm_db2"
    description = "IBM Db2 database connector"

    def connect(self) -> None:
        raise NotImplementedError("IBM Db2 connector: install 'ibm-db' package")

    def close(self) -> None:
        pass


registry.register("databases", "ibm_db2", IBMDB2Connector)
