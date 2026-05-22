from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class NetSuiteConnector(SyncConnector):
    name = "netsuite"
    description = "NetSuite CRM connector"

    def connect(self) -> None:
        raise NotImplementedError("NetSuite connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("NetSuite connector is not implemented yet")


registry.register("crm", "netsuite", NetSuiteConnector)
