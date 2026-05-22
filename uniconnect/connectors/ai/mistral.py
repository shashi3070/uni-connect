from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    from mistralai import Mistral
except ImportError:
    Mistral = None


class MistralConnector(SyncConnector):
    name = "mistral"
    description = "Mistral AI connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if Mistral is None:
            raise ImportError("mistralai is required. Install with: pip install mistralai")

        api_key = self.config.get("api_key")
        server_url = self.config.get("server_url")
        kwargs = {"api_key": api_key}
        if server_url:
            kwargs["server_url"] = server_url
        self._client = Mistral(**kwargs)
        self._connected = True

    def close(self) -> None:
        self._client = None
        self._connected = False

    def _get_model(self) -> str:
        return self.config.get("model", "mistral-large-latest")

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")

    def complete(self, messages: list[dict], **kwargs: Any) -> dict:
        self._ensure_connected()
        model = self._get_model()
        resp = self._client.chat.complete(
            model=model,
            messages=messages,
            **kwargs,
        )
        return resp.model_dump()


registry.register("ai", "mistral", MistralConnector)
