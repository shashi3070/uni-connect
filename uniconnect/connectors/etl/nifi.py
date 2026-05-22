from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError


class NiFiConnector(SyncConnector):
    name = "nifi"
    description = "Apache NiFi data flow automation"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._session = None
        self._base_url = ""

    def connect(self) -> None:
        try:
            import requests
        except ImportError:
            raise ImportError("requests is required. Install with: pip install requests")

        host = self.config.get("host", "localhost")
        port = self.config.get("port", 8080)
        self._base_url = f"http://{host}:{port}/nifi-api"

        self._session = requests.Session()
        username = self.config.get("username", "")
        password = self.config.get("password", "")

        if username and password:
            resp = self._session.post(
                f"{self._base_url}/access/token",
                data={"username": username, "password": password},
            )
            resp.raise_for_status()
            token = resp.text
            self._session.headers.update({"Authorization": f"Bearer {token}"})

        self._session.headers.update({"Content-Type": "application/json"})
        self._connected = True

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None
        self._connected = False

    def list_process_groups(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.get(f"{self._base_url}/process-groups/root/process-groups")
        resp.raise_for_status()
        return resp.json().get("processGroups", [])

    def list_processors(self, process_group_id: str = "root") -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.get(
            f"{self._base_url}/process-groups/{process_group_id}/processors",
        )
        resp.raise_for_status()
        return resp.json().get("processors", [])

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("etl", "nifi", NiFiConnector)
