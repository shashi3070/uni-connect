from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class MetabaseConnector(SyncConnector):
    name = "metabase"
    description = "Metabase"

    def connect(self) -> None:
        raise NotImplementedError("Metabase connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Metabase connector is not yet implemented")


registry.register("business_intelligence", "metabase", MetabaseConnector)
