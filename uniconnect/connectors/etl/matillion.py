from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import requests
except ImportError:
    requests = None


class MatillionConnector(SyncConnector):
    name = "matillion"
    description = "Matillion ETL data transformation platform"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._session = None
        self._base_url = ""

    def connect(self) -> None:
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")

        self._base_url = self.config.get("base_url", "").rstrip("/")
        api_key = self.config.get("api_key", "")
        self._session = requests.Session()
        self._session.headers.update({
            "x-api-key": api_key,
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
        project_id = self.config.get("project_id", "")
        environment = self.config.get("environment_name", "")
        url = f"{self._base_url}/api/v1/project/{project_id}/environment/{environment}/jobs"
        resp = self._session.get(url)
        resp.raise_for_status()
        return resp.json().get("jobs", [])

    def run_job(self, job_name: str) -> dict[str, Any]:
        self._ensure_connected()
        project_id = self.config.get("project_id", "")
        environment = self.config.get("environment_name", "")
        url = f"{self._base_url}/api/v1/project/{project_id}/environment/{environment}/job/{job_name}/run"
        resp = self._session.post(url)
        resp.raise_for_status()
        return resp.json()

    def get_job_status(self, run_id: str) -> dict[str, Any]:
        self._ensure_connected()
        project_id = self.config.get("project_id", "")
        environment = self.config.get("environment_name", "")
        url = f"{self._base_url}/api/v1/project/{project_id}/environment/{environment}/run/{run_id}"
        resp = self._session.get(url)
        resp.raise_for_status()
        return resp.json()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("etl", "matillion", MatillionConnector)
