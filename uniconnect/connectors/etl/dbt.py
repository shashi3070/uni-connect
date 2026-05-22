from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import requests
except ImportError:
    requests = None


class DBTConnector(SyncConnector):
    name = "dbt"
    description = "dbt data build tool cloud"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._session = None
        self._base_url = ""

    def connect(self) -> None:
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")

        self._base_url = self.config.get("api_url", "https://cloud.getdbt.com/api/v2").rstrip("/")
        service_token = self.config.get("service_token", "")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {service_token}",
            "Content-Type": "application/json",
        })
        self._connected = True

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None
        self._connected = False

    def list_jobs(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        account_id = self.config.get("account_id", "")
        resp = self._session.get(f"{self._base_url}/accounts/{account_id}/jobs")
        resp.raise_for_status()
        return resp.json().get("data", [])

    def run_job(self, job_id: str) -> dict[str, Any]:
        self._ensure_connected()
        account_id = self.config.get("account_id", "")
        resp = self._session.post(
            f"{self._base_url}/accounts/{account_id}/jobs/{job_id}/run",
        )
        resp.raise_for_status()
        return resp.json().get("data", {})

    def get_run_status(self, run_id: str) -> dict[str, Any]:
        self._ensure_connected()
        account_id = self.config.get("account_id", "")
        resp = self._session.get(
            f"{self._base_url}/accounts/{account_id}/runs/{run_id}",
        )
        resp.raise_for_status()
        return resp.json().get("data", {})

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("etl", "dbt", DBTConnector)
