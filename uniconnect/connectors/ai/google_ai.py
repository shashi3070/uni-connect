from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class GoogleAIConnector(SyncConnector):
    name = "google_ai"
    description = "Google Gemini AI connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._model = None

    def connect(self) -> None:
        if genai is None:
            raise ImportError("google-generativeai is required. Install with: pip install google-generativeai")

        api_key = self.config.get("api_key")
        genai.configure(api_key=api_key)
        model_name = self.config.get("model", "gemini-pro")
        self._model = genai.GenerativeModel(model_name)
        self._connected = True

    def close(self) -> None:
        self._model = None
        self._connected = False

    def _get_model(self) -> str:
        return self.config.get("model", "gemini-pro")

    def complete(self, messages: list[dict], **kwargs: Any) -> dict:
        self._ensure_connected()
        resp = self._model.generate_content(messages, **kwargs)
        return {"text": resp.text, "candidates": [c.to_dict() for c in resp.candidates]}

    def stream_complete(self, messages: list[dict], **kwargs: Any):
        self._ensure_connected()
        stream = self._model.generate_content(messages, stream=True, **kwargs)
        for chunk in stream:
            yield {"text": chunk.text, "candidates": [c.to_dict() for c in chunk.candidates]}

    def generate_image(self, prompt: str, **kwargs: Any) -> dict:
        self._ensure_connected()
        model_name = self.config.get("image_model", "imagen-3.0-generate-001")
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content(prompt, **kwargs)
        return {"text": resp.text, "candidates": [c.to_dict() for c in resp.candidates]}

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("ai", "google_ai", GoogleAIConnector)
