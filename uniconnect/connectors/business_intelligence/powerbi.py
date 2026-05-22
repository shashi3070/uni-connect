from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class PowerBIConnector(SyncConnector):
    name = "powerbi"
    description = "Microsoft Power BI"

    def connect(self) -> None:
        raise NotImplementedError("Power BI connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Power BI connector is not yet implemented")


registry.register("business_intelligence", "powerbi", PowerBIConnector)
