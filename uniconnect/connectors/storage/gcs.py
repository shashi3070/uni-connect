from __future__ import annotations

import io
from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    from google.cloud import storage as gcs_storage
except ImportError:
    gcs_storage = None


class GCSConnector(SyncConnector):
    name = "gcs"
    description = "Google Cloud Storage"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None
        self._bucket = None

    def connect(self) -> None:
        if gcs_storage is None:
            raise ImportError(
                "google-cloud-storage is required. Install with: pip install google-cloud-storage"
            )

        credentials_path = self.config.get("credentials_path")
        project = self.config.get("project")

        if credentials_path:
            self._client = gcs_storage.Client.from_service_account_json(
                credentials_path, project=project
            )
        else:
            self._client = gcs_storage.Client(project=project)

        bucket_name = self.config.get("bucket", "")
        self._bucket = self._client.bucket(bucket_name)
        self._connected = True

    def close(self) -> None:
        self._client = None
        self._bucket = None
        self._connected = False

    def list_files(self, prefix: str = "") -> list[str]:
        self._ensure_connected()
        blobs = self._client.list_blobs(self._bucket, prefix=prefix)
        return [blob.name for blob in blobs]

    def read_file(self, path: str) -> bytes:
        self._ensure_connected()
        blob = self._bucket.blob(path)
        return blob.download_as_bytes()

    def write_file(self, path: str, data: bytes) -> None:
        self._ensure_connected()
        blob = self._bucket.blob(path)
        blob.upload_from_string(data)

    def delete_file(self, path: str) -> None:
        self._ensure_connected()
        blob = self._bucket.blob(path)
        blob.delete()

    def file_exists(self, path: str) -> bool:
        self._ensure_connected()
        blob = self._bucket.blob(path)
        return blob.exists()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("storage", "gcs", GCSConnector)
registry.register("storage", "gcs", GCSConnector, driver="google-cloud-storage")
