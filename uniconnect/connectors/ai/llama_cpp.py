from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class LlamaCppConnector(SyncConnector):
    name = "llama_cpp"
    description = "llama.cpp connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)

    def connect(self) -> None:
        raise NotImplementedError("llama.cpp connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("llama.cpp connector is not implemented yet")

    def complete(self, messages: list[dict], **kwargs: Any) -> dict:
        raise NotImplementedError("llama.cpp connector is not implemented yet")


registry.register("ai", "llama_cpp", LlamaCppConnector)
