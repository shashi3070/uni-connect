from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class PerplexityConnector(SyncConnector):
    name = "perplexity"
    description = "Perplexity AI connector (OpenAI-compatible)"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)

    def connect(self) -> None:
        raise NotImplementedError("Perplexity AI connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Perplexity AI connector is not implemented yet")

    def complete(self, messages: list[dict], **kwargs: Any) -> dict:
        raise NotImplementedError("Perplexity AI connector is not implemented yet")


registry.register("ai", "perplexity", PerplexityConnector)
