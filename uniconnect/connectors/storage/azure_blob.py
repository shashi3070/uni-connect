from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    BlobServiceClient = None


class AzureBlobConnector(SyncConnector):
    name = "azure_blob"
    description = "Azure Blob Storage"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._service_client = None
        self._container_client = None

    def connect(self) -> None:
        if BlobServiceClient is None:
            raise ImportError(
                "azure-storage-blob is required. Install with: pip install azure-storage-blob"
            )

        connection_string = self.config.get("connection_string")
        container_name = self.config.get("container_name", "")

        self._service_client = BlobServiceClient.from_connection_string(connection_string)
        self._container_client = self._service_client.get_container_client(container_name)
        self._connected = True

    def close(self) -> None:
        self._service_client = None
        self._container_client = None
        self._connected = False

    def list_files(self, prefix: str = "") -> list[str]:
        self._ensure_connected()
        blobs = self._container_client.list_blobs(name_starts_with=prefix)
        return [blob.name for blob in blobs]

    def read_file(self, path: str) -> bytes:
        self._ensure_connected()
        blob_client = self._container_client.get_blob_client(path)
        return blob_client.download_blob().readall()

    def write_file(self, path: str, data: bytes) -> None:
        self._ensure_connected()
        blob_client = self._container_client.get_blob_client(path)
        blob_client.upload_blob(data, overwrite=True)

    def delete_file(self, path: str) -> None:
        self._ensure_connected()
        blob_client = self._container_client.get_blob_client(path)
        blob_client.delete_blob()

    def file_exists(self, path: str) -> bool:
        self._ensure_connected()
        blob_client = self._container_client.get_blob_client(path)
        try:
            blob_client.get_blob_properties()
            return True
        except Exception:
            return False

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("storage", "azure_blob", AzureBlobConnector)
