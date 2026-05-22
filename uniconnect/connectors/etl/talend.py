from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError


class TalendConnector(SyncConnector):
    name = "talend"
    description = "Talend data integration platform"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._session = None
        self._base_url = ""

    def connect(self) -> None:
        try:
            import requests
        except ImportError:
            raise ImportError("requests is required. Install with: pip install requests")

        self._base_url = self.config.get("base_url", "https://api.talend.com").rstrip("/")
        api_token = self.config.get("api_token", "")

        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        })
        self._connected = True

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None
        self._connected = False

    def list_executables(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.get(f"{self._base_url}/executables")
        resp.raise_for_status()
        return resp.json().get("data", [])

    def run_executable(self, executable_id: str) -> dict[str, Any]:
        self._ensure_connected()
        resp = self._session.post(f"{self._base_url}/executables/{executable_id}/run")
        resp.raise_for_status()
        return resp.json()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("etl", "talend", TalendConnector)
