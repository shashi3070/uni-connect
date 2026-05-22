from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import replicate
except ImportError:
    replicate = None


class ReplicateConnector(SyncConnector):
    name = "replicate"
    description = "Replicate connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if replicate is None:
            raise ImportError("replicate is required. Install with: pip install replicate")

        api_token = self.config.get("api_token")
        self._client = replicate.Client(api_token=api_token)
        self._connected = True

    def close(self) -> None:
        self._client = None
        self._connected = False

    def _get_model(self) -> str:
        return self.config.get("model", "meta/meta-llama-3-70b-instruct")

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")

    def run(self, input: dict, **kwargs: Any) -> Any:
        self._ensure_connected()
        model = self._get_model()
        return self._client.run(model, input=input, **kwargs)


registry.register("ai", "replicate", ReplicateConnector)
