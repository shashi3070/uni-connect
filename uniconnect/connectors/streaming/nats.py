from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class NATSConnector(SyncConnector):
    name = "nats"
    description = "NATS messaging"

    def connect(self) -> None:
        raise NotImplementedError("NATS connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("NATS connector is not yet implemented")


registry.register("streaming", "nats", NATSConnector)
