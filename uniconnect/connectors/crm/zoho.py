from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class ZohoConnector(SyncConnector):
    name = "zoho"
    description = "Zoho CRM connector"

    def connect(self) -> None:
        raise NotImplementedError("Zoho connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Zoho connector is not implemented yet")


registry.register("crm", "zoho", ZohoConnector)
