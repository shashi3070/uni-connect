from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class NotionConnector(SyncConnector):
    name = "notion"
    description = "Notion"

    def connect(self) -> None:
        raise NotImplementedError("Notion connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Notion connector is not yet implemented")


registry.register("collaboration", "notion", NotionConnector)
