from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class ModeConnector(SyncConnector):
    name = "mode"
    description = "Mode Analytics"

    def connect(self) -> None:
        raise NotImplementedError("Mode Analytics connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Mode Analytics connector is not yet implemented")


registry.register("business_intelligence", "mode", ModeConnector)
