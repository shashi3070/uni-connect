from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class SAPCRMConnector(SyncConnector):
    name = "sap_crm"
    description = "SAP CRM connector"

    def connect(self) -> None:
        raise NotImplementedError("SAP CRM connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("SAP CRM connector is not implemented yet")


registry.register("crm", "sap_crm", SAPCRMConnector)
