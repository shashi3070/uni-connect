from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import openai
except ImportError:
    openai = None


class OpenAIConnector(SyncConnector):
    name = "openai"
    description = "OpenAI and Azure OpenAI connectors"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None
        self._azure_client = None

    def connect(self) -> None:
        if openai is None:
            raise ImportError("openai is required. Install with: pip install openai")

        api_key = self.config.get("api_key")
        base_url = self.config.get("base_url")
        azure = self.config.get("azure", False)

        if azure:
            self._azure_client = openai.AzureOpenAI(
                api_key=api_key,
                azure_endpoint=base_url,
                api_version=self.config.get("api_version", "2024-02-15-preview"),
            )
        else:
            kwargs = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url
            self._client = openai.OpenAI(**kwargs)

        self._connected = True

    def close(self) -> None:
        self._client = None
        self._azure_client = None
        self._connected = False

    def _get_client(self):
        return self._azure_client if self._azure_client else self._client

    def _get_model(self) -> str:
        return self.config.get("model", "gpt-4o")

    def complete(self, messages: list[dict], **kwargs: Any) -> dict:
        self._ensure_connected()
        client = self._get_client()
        model = self._get_model()
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        return resp.model_dump()

    def stream_complete(self, messages: list[dict], **kwargs: Any):
        self._ensure_connected()
        client = self._get_client()
        model = self._get_model()
        kwargs["stream"] = True
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        for chunk in stream:
            yield chunk.model_dump()

    def embed(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        self._ensure_connected()
        client = self._get_client()
        model = self.config.get("embedding_model", "text-embedding-ada-002")
        resp = client.embeddings.create(model=model, input=texts, **kwargs)
        return [item.embedding for item in resp.data]

    def models(self) -> list[str]:
        self._ensure_connected()
        client = self._get_client()
        return [m.id for m in client.models.list()]

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("ai", "openai", OpenAIConnector)
registry.register("ai", "openai", OpenAIConnector, driver="azure")
