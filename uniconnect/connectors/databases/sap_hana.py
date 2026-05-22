from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class SAPHanaConnector(SyncConnector):
    name = "sap_hana"
    description = "SAP HANA database connector"

    def connect(self) -> None:
        raise NotImplementedError("SAP HANA connector: install 'hdbcli' package")

    def close(self) -> None:
        pass


registry.register("databases", "sap_hana", SAPHanaConnector)
