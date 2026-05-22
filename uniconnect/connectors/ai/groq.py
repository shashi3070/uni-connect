from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class GroqConnector(SyncConnector):
    name = "groq"
    description = "Groq connector (OpenAI-compatible)"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if OpenAI is None:
            raise ImportError("openai is required. Install with: pip install openai")

        api_key = self.config.get("api_key")
        base_url = self.config.get("base_url", "https://api.groq.com/openai/v1")
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._connected = True

    def close(self) -> None:
        self._client = None
        self._connected = False

    def _get_model(self) -> str:
        return self.config.get("model", "llama3-70b-8192")

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")

    def complete(self, messages: list[dict], **kwargs: Any) -> dict:
        self._ensure_connected()
        model = self._get_model()
        resp = self._client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        return resp.model_dump()


registry.register("ai", "groq", GroqConnector)
