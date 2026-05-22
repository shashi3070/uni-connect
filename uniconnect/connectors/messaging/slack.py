from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import requests
except ImportError:
    requests = None


class SlackConnector(SyncConnector):
    name = "slack"
    description = "Slack messaging connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._token = ""
        self._base_url = "https://slack.com/api"

    def connect(self) -> None:
        self._token = self.config.get("token", "")
        if not self._token:
            raise ValueError("token is required for Slack connector")
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")
        self._connected = True

    def close(self) -> None:
        self._connected = False

    def post_message(self, channel: str, text: str) -> dict:
        self._ensure_connected()
        resp = requests.post(
            f"{self._base_url}/chat.postMessage",
            headers={"Authorization": f"Bearer {self._token}"},
            json={"channel": channel, "text": text},
        )
        resp.raise_for_status()
        return resp.json()

    def list_channels(self) -> list[dict]:
        self._ensure_connected()
        resp = requests.get(
            f"{self._base_url}/conversations.list",
            headers={"Authorization": f"Bearer {self._token}"},
        )
        resp.raise_for_status()
        return resp.json().get("channels", [])

    def upload_file(self, channel: str, file_path: str) -> dict:
        self._ensure_connected()
        with open(file_path, "rb") as f:
            resp = requests.post(
                f"{self._base_url}/files.upload",
                headers={"Authorization": f"Bearer {self._token}"},
                files={"file": f},
                data={"channels": channel},
            )
        resp.raise_for_status()
        return resp.json()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("messaging", "slack", SlackConnector)
