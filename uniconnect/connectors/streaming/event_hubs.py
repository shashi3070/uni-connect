from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class EventHubsConnector(SyncConnector):
    name = "event_hubs"
    description = "Azure Event Hubs"

    def connect(self) -> None:
        raise NotImplementedError("Event Hubs connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Event Hubs connector is not yet implemented")


registry.register("streaming", "event_hubs", EventHubsConnector)
