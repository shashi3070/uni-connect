from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class IntercomConnector(SyncConnector):
    name = "intercom"
    description = "Intercom CRM connector"

    def connect(self) -> None:
        raise NotImplementedError("Intercom connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Intercom connector is not implemented yet")


registry.register("crm", "intercom", IntercomConnector)
