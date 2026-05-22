from __future__ import annotations

import json
from typing import Any, Optional

import requests

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class OllamaConnector(SyncConnector):
    name = "ollama"
    description = "Ollama local LLM connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._base_url = self.config.get("base_url", "http://localhost:11434")

    def connect(self) -> None:
        self._connected = True

    def close(self) -> None:
        self._connected = False

    def _get_model(self) -> str:
        return self.config.get("model", "llama3")

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")

    def complete(self, messages: list[dict], **kwargs: Any) -> dict:
        self._ensure_connected()
        model = self._get_model()
        resp = requests.post(
            f"{self._base_url}/api/chat",
            json={"model": model, "messages": messages, "stream": False, **kwargs},
        )
        resp.raise_for_status()
        return resp.json()

    def stream_complete(self, messages: list[dict], **kwargs: Any):
        self._ensure_connected()
        model = self._get_model()
        resp = requests.post(
            f"{self._base_url}/api/chat",
            json={"model": model, "messages": messages, "stream": True, **kwargs},
            stream=True,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                yield json.loads(line)

    def list_models(self) -> list[dict]:
        self._ensure_connected()
        resp = requests.get(f"{self._base_url}/api/tags")
        resp.raise_for_status()
        return resp.json().get("models", [])

    def pull_model(self, name: str) -> dict:
        self._ensure_connected()
        resp = requests.post(f"{self._base_url}/api/pull", json={"name": name})
        resp.raise_for_status()
        return resp.json()


registry.register("ai", "ollama", OllamaConnector)
