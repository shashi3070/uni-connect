from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import requests
except ImportError:
    requests = None


class AirbyteConnector(SyncConnector):
    name = "airbyte"
    description = "Airbyte data integration platform"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._session = None
        self._base_url = ""

    def connect(self) -> None:
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")

        host = self.config.get("host", "localhost")
        port = self.config.get("port", 8001)
        api_key = self.config.get("api_key", "")
        self._base_url = f"http://{host}:{port}/api/v1"

        self._session = requests.Session()
        if api_key:
            self._session.headers.update({"Authorization": f"Bearer {api_key}"})
        self._session.headers.update({"Content-Type": "application/json"})
        self._connected = True

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None
        self._connected = False

    def list_workspaces(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.post(f"{self._base_url}/workspaces/list")
        resp.raise_for_status()
        return resp.json().get("workspaces", [])

    def list_sources(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.post(f"{self._base_url}/sources/list")
        resp.raise_for_status()
        return resp.json().get("sources", [])

    def list_destinations(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.post(f"{self._base_url}/destinations/list")
        resp.raise_for_status()
        return resp.json().get("destinations", [])

    def sync(self, connection_id: str) -> dict[str, Any]:
        self._ensure_connected()
        resp = self._session.post(
            f"{self._base_url}/connections/sync",
            json={"connectionId": connection_id},
        )
        resp.raise_for_status()
        return resp.json()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("etl", "airbyte", AirbyteConnector)
