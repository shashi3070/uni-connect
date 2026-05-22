from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import anthropic
except ImportError:
    anthropic = None


class AnthropicConnector(SyncConnector):
    name = "anthropic"
    description = "Anthropic Claude connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if anthropic is None:
            raise ImportError("anthropic is required. Install with: pip install anthropic")

        api_key = self.config.get("api_key")
        base_url = self.config.get("base_url")
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = anthropic.Anthropic(**kwargs)
        self._connected = True

    def close(self) -> None:
        self._client = None
        self._connected = False

    def _get_model(self) -> str:
        return self.config.get("model", "claude-sonnet-4-20250514")

    def complete(self, messages: list[dict], **kwargs: Any) -> dict:
        self._ensure_connected()
        model = self._get_model()
        resp = self._client.messages.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        return resp.model_dump()

    def stream_complete(self, messages: list[dict], **kwargs: Any):
        self._ensure_connected()
        model = self._get_model()
        kwargs["stream"] = True
        stream = self._client.messages.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        for chunk in stream:
            yield chunk.model_dump()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("ai", "anthropic", AnthropicConnector)
