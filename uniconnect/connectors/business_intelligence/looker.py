from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class LookerConnector(SyncConnector):
    name = "looker"
    description = "Looker"

    def connect(self) -> None:
        raise NotImplementedError("Looker connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Looker connector is not yet implemented")


registry.register("business_intelligence", "looker", LookerConnector)
