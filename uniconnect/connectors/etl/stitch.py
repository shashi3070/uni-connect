from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError


class StitchConnector(SyncConnector):
    name = "stitch"
    description = "Stitch data pipeline ETL platform"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._session = None

    def connect(self) -> None:
        try:
            import requests
        except ImportError:
            raise ImportError("requests is required. Install with: pip install requests")

        client_id = self.config.get("client_id", "")
        access_token = self.config.get("access_token", "")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        })
        self._base_url = f"https://api.stitchdata.com/v4/{client_id}"
        self._connected = True

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None
        self._connected = False

    def list_sources(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.get(f"{self._base_url}/sources")
        resp.raise_for_status()
        return resp.json().get("sources", [])

    def list_extractions(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._session.get(f"{self._base_url}/extractions")
        resp.raise_for_status()
        return resp.json().get("extractions", [])

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("etl", "stitch", StitchConnector)
