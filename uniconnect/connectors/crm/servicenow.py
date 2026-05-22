from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class ServiceNowConnector(SyncConnector):
    name = "servicenow"
    description = "ServiceNow CRM connector"

    def connect(self) -> None:
        raise NotImplementedError("ServiceNow connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("ServiceNow connector is not implemented yet")


registry.register("crm", "servicenow", ServiceNowConnector)
