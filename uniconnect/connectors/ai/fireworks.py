from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class FireworksConnector(SyncConnector):
    name = "fireworks"
    description = "Fireworks AI connector (OpenAI-compatible)"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)

    def connect(self) -> None:
        raise NotImplementedError("Fireworks AI connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Fireworks AI connector is not implemented yet")

    def complete(self, messages: list[dict], **kwargs: Any) -> dict:
        raise NotImplementedError("Fireworks AI connector is not implemented yet")


registry.register("ai", "fireworks", FireworksConnector)
