from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

try:
    from google.oauth2 import service_account
except ImportError:
    service_account = None


class BigQueryConnector(SyncConnector):
    name = "bigquery"
    description = "Google BigQuery data warehouse"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if bigquery is None:
            raise ImportError("google-cloud-bigquery is required. Install with: pip install google-cloud-bigquery")

        project = self.config.get("project", "")
        credentials_path = self.config.get("credentials_path", "")

        if credentials_path:
            if service_account is None:
                raise ImportError("google-auth is required. Install with: pip install google-auth")
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self._client = bigquery.Client(project=project, credentials=credentials)
        else:
            self._client = bigquery.Client(project=project)

        self._connected = True

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
        self._connected = False

    def query(self, sql: str) -> list[dict[str, Any]]:
        self._ensure_connected()
        job = self._client.query(sql)
        rows = job.result()
        return [dict(row.items()) for row in rows]

    def execute(self, sql: str) -> int:
        self._ensure_connected()
        job = self._client.query(sql)
        return job.result().total_rows or 0

    def load_from_gcs(self, table: str, gcs_uri: str, **kwargs: Any) -> None:
        self._ensure_connected()
        dataset = self.config.get("dataset", "")
        table_ref = f"{dataset}.{table}"
        job_config = bigquery.LoadJobConfig(
            source_format=kwargs.get("source_format", bigquery.SourceFormat.CSV),
            autodetect=kwargs.get("autodetect", True),
        )
        load_job = self._client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
        load_job.result()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("warehouse", "bigquery", BigQueryConnector)
