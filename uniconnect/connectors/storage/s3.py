from __future__ import annotations

import io
from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import boto3
except ImportError:
    boto3 = None

try:
    import s3fs
except ImportError:
    s3fs = None

try:
    import aioboto3
except ImportError:
    aioboto3 = None


class S3Connector(SyncConnector):
    name = "s3"
    description = "Amazon S3 and S3-compatible storage"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None
        self._fs = None

    def connect(self) -> None:
        driver = self.config.get("driver", "boto3")
        self.bucket = self.config.get("bucket", "")

        if driver == "boto3":
            if boto3 is None:
                raise ImportError("boto3 is required. Install with: pip install boto3")
            self._client = boto3.client(
                "s3",
                aws_access_key_id=self.config.get("aws_access_key_id"),
                aws_secret_access_key=self.config.get("aws_secret_access_key"),
                region_name=self.config.get("region"),
                endpoint_url=self.config.get("endpoint_url"),
            )
        elif driver == "s3fs":
            if s3fs is None:
                raise ImportError("s3fs is required. Install with: pip install s3fs")
            self._fs = s3fs.S3FileSystem(
                key=self.config.get("aws_access_key_id"),
                secret=self.config.get("aws_secret_access_key"),
                endpoint_url=self.config.get("endpoint_url"),
            )
        elif driver == "aioboto3":
            if aioboto3 is None:
                raise ImportError("aioboto3 is required. Install with: pip install aioboto3")
            self._client = "aioboto3"
        else:
            raise ValueError(f"Unsupported driver: {driver}")

        self._connected = True

    def close(self) -> None:
        if self._client and self._client != "aioboto3":
            self._client.close()
        self._client = None
        self._fs = None
        self._connected = False

    def list_files(self, prefix: str = "") -> list[str]:
        self._ensure_connected()
        driver = self.config.get("driver", "boto3")

        if driver == "boto3" or driver == "aioboto3":
            paginator = self._client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket, Prefix=prefix)
            files = []
            for page in pages:
                for obj in page.get("Contents", []):
                    files.append(obj["Key"])
            return files
        elif driver == "s3fs":
            path = f"{self.bucket}/{prefix}" if prefix else self.bucket
            return self._fs.ls(path)

        return []

    def read_file(self, path: str) -> bytes:
        self._ensure_connected()
        driver = self.config.get("driver", "boto3")

        if driver == "boto3" or driver == "aioboto3":
            resp = self._client.get_object(Bucket=self.bucket, Key=path)
            return resp["Body"].read()
        elif driver == "s3fs":
            with self._fs.open(f"{self.bucket}/{path}", "rb") as f:
                return f.read()

        raise NotImplementedError(f"read_file not implemented for driver: {driver}")

    def write_file(self, path: str, data: bytes) -> None:
        self._ensure_connected()
        driver = self.config.get("driver", "boto3")

        if driver == "boto3" or driver == "aioboto3":
            self._client.put_object(Bucket=self.bucket, Key=path, Body=data)
        elif driver == "s3fs":
            with self._fs.open(f"{self.bucket}/{path}", "wb") as f:
                f.write(data)

    def delete_file(self, path: str) -> None:
        self._ensure_connected()
        driver = self.config.get("driver", "boto3")

        if driver == "boto3" or driver == "aioboto3":
            self._client.delete_object(Bucket=self.bucket, Key=path)
        elif driver == "s3fs":
            self._fs.rm(f"{self.bucket}/{path}")

    def file_exists(self, path: str) -> bool:
        self._ensure_connected()
        driver = self.config.get("driver", "boto3")

        if driver == "boto3" or driver == "aioboto3":
            try:
                self._client.head_object(Bucket=self.bucket, Key=path)
                return True
            except Exception:
                return False
        elif driver == "s3fs":
            return self._fs.exists(f"{self.bucket}/{path}")

        return False

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("storage", "s3", S3Connector)
registry.register("storage", "s3", S3Connector, driver="boto3")
registry.register("storage", "s3", S3Connector, driver="s3fs")
