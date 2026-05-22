from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class ConfluenceConnector(SyncConnector):
    name = "confluence"
    description = "Atlassian Confluence"

    def connect(self) -> None:
        raise NotImplementedError("Confluence connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Confluence connector is not yet implemented")


registry.register("collaboration", "confluence", ConfluenceConnector)
