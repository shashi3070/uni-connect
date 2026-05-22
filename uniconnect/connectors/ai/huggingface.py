from __future__ import annotations

from typing import Any, Optional

import requests

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import huggingface_hub
except ImportError:
    huggingface_hub = None


class HuggingFaceConnector(SyncConnector):
    name = "huggingface"
    description = "Hugging Face connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._headers = {}

    def connect(self) -> None:
        api_token = self.config.get("api_token")
        if api_token:
            self._headers["Authorization"] = f"Bearer {api_token}"
        self._connected = True

    def close(self) -> None:
        self._headers = {}
        self._connected = False

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")

    def _get_model(self) -> str:
        return self.config.get("model", "gpt2")

    def inference(self, inputs: Any, **kwargs: Any) -> dict:
        self._ensure_connected()
        endpoint_url = self.config.get("endpoint_url")
        if endpoint_url:
            resp = requests.post(
                endpoint_url,
                headers={**self._headers, "Content-Type": "application/json"},
                json={"inputs": inputs, **kwargs},
            )
            resp.raise_for_status()
            return resp.json()

        if huggingface_hub is None:
            raise ImportError("huggingface-hub is required. Install with: pip install huggingface-hub")

        api_token = self.config.get("api_token")
        model = self._get_model()
        api = huggingface_hub.InferenceClient(token=api_token)
        resp = api.post(json={"inputs": inputs, **kwargs}, model=model)
        return resp.json()

    def list_models(self, **kwargs: Any) -> list[dict]:
        if huggingface_hub is None:
            raise ImportError("huggingface-hub is required. Install with: pip install huggingface-hub")

        api_token = self.config.get("api_token")
        api = huggingface_hub.HfApi(token=api_token)
        models = api.list_models(**kwargs)
        return [m.modelId for m in models]


registry.register("ai", "huggingface", HuggingFaceConnector)
