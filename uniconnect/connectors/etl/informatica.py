from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError


class InformaticaConnector(SyncConnector):
    name = "informatica"
    description = "Informatica Intelligent Data Management Cloud"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._session = None
        self._base_url = ""

    def connect(self) -> None:
        try:
            import requests
        except ImportError:
            raise ImportError("requests is required. Install with: pip install requests")

        self._base_url = self.config.get("base_url", "https://api.informatica.cloud").rstrip("/")
        username = self.config.get("username", "")
        password = self.config.get("password", "")

        self._session = requests.Session()
        resp = self._session.post(
            f"{self._base_url}/saas/public/core/v3/login",
            json={"username": username, "password": password},
        )
        resp.raise_for_status()
        token = resp.json().get("access_token", "")
        self._session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })
        self._connected = True

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None
        self._connected = False

    def list_connections(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.get(f"{self._base_url}/saas/public/core/v3/connection")
        resp.raise_for_status()
        return resp.json().get("items", [])

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("etl", "informatica", InformaticaConnector)
