from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    from minio import Minio
except ImportError:
    Minio = None


class MinioConnector(SyncConnector):
    name = "minio"
    description = "MinIO storage (S3-compatible)"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None
        self._bucket = ""

    def connect(self) -> None:
        if Minio is None:
            raise ImportError(
                "minio is required. Install with: pip install minio"
            )

        endpoint = self.config.get("endpoint", self.config.get("endpoint_url", ""))
        access_key = self.config.get("access_key", self.config.get("aws_access_key_id", ""))
        secret_key = self.config.get("secret_key", self.config.get("aws_secret_access_key", ""))
        secure = self.config.get("secure", True)
        region = self.config.get("region")

        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            region=region,
        )
        self._bucket = self.config.get("bucket", "")
        bucket_exists = self._client.bucket_exists(self._bucket)
        if not bucket_exists:
            self._client.make_bucket(self._bucket)
        self._connected = True

    def close(self) -> None:
        self._client = None
        self._connected = False

    def list_files(self, prefix: str = "") -> list[str]:
        self._ensure_connected()
        objects = self._client.list_objects(self._bucket, prefix=prefix, recursive=True)
        return [obj.object_name for obj in objects]

    def read_file(self, path: str) -> bytes:
        self._ensure_connected()
        resp = self._client.get_object(self._bucket, path)
        data = resp.read()
        resp.close()
        resp.release_conn()
        return data

    def write_file(self, path: str, data: bytes) -> None:
        self._ensure_connected()
        from io import BytesIO
        length = len(data)
        self._client.put_object(
            self._bucket, path, BytesIO(data), length
        )

    def delete_file(self, path: str) -> None:
        self._ensure_connected()
        self._client.remove_object(self._bucket, path)

    def file_exists(self, path: str) -> bool:
        self._ensure_connected()
        try:
            self._client.stat_object(self._bucket, path)
            return True
        except Exception:
            return False

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("storage", "minio", MinioConnector)
