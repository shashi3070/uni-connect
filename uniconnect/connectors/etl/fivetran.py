from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import requests
except ImportError:
    requests = None


class FivetranConnector(SyncConnector):
    name = "fivetran"
    description = "Fivetran automated data movement platform"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._session = None
        self._base_url = "https://api.fivetran.com/v1"

    def connect(self) -> None:
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")

        api_key = self.config.get("api_key", "")
        api_secret = self.config.get("api_secret", "")
        self._session = requests.Session()
        self._session.auth = (api_key, api_secret)
        self._session.headers.update({"Content-Type": "application/json"})
        self._connected = True

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None
        self._connected = False

    def list_connectors(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.get(f"{self._base_url}/connectors")
        resp.raise_for_status()
        return resp.json().get("data", {}).get("items", [])

    def list_destinations(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.get(f"{self._base_url}/destinations")
        resp.raise_for_status()
        return resp.json().get("data", {}).get("items", [])

    def sync(self, connector_id: str) -> dict[str, Any]:
        self._ensure_connected()
        resp = self._session.post(f"{self._base_url}/connectors/{connector_id}/force")
        resp.raise_for_status()
        return resp.json()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("etl", "fivetran", FivetranConnector)
