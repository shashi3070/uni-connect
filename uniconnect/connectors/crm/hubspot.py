from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import requests
except ImportError:
    requests = None


class HubSpotConnector(SyncConnector):
    name = "hubspot"
    description = "HubSpot CRM connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._session = None
        self._base_url = "https://api.hubapi.com"

    def connect(self) -> None:
        access_token = self.config.get("access_token", "")
        if not access_token:
            raise ValueError("access_token is required for HubSpot connector")
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        })
        self._connected = True

    def close(self) -> None:
        if self._session:
            self._session.close()
        self._session = None
        self._connected = False

    def get_contacts(self) -> list[dict]:
        self._ensure_connected()
        resp = self._session.get(f"{self._base_url}/crm/v3/objects/contacts")
        resp.raise_for_status()
        return resp.json().get("results", [])

    def get_deals(self) -> list[dict]:
        self._ensure_connected()
        resp = self._session.get(f"{self._base_url}/crm/v3/objects/deals")
        resp.raise_for_status()
        return resp.json().get("results", [])

    def create_contact(self, data: dict) -> dict:
        self._ensure_connected()
        resp = self._session.post(
            f"{self._base_url}/crm/v3/objects/contacts",
            json={"properties": data},
        )
        resp.raise_for_status()
        return resp.json()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("crm", "hubspot", HubSpotConnector)
