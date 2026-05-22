from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import boto3
except ImportError:
    boto3 = None


class DynamoDBConnector(SyncConnector):
    name = "dynamodb"
    description = "Amazon DynamoDB database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None
        self._resource = None

    def connect(self) -> None:
        if boto3 is None:
            raise ImportError("boto3 is required. Install with: pip install boto3")

        region = self.config.get("region", "us-east-1")
        endpoint_url = self.config.get("endpoint_url", None)

        self._client = boto3.client(
            "dynamodb",
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id=self.config.get("aws_access_key_id"),
            aws_secret_access_key=self.config.get("aws_secret_access_key"),
        )
        self._resource = boto3.resource(
            "dynamodb",
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id=self.config.get("aws_access_key_id"),
            aws_secret_access_key=self.config.get("aws_secret_access_key"),
        )
        self._connected = True

    def close(self) -> None:
        self._client = None
        self._resource = None
        self._connected = False

    def get_item(self, table_name: str, key: dict) -> Optional[dict[str, Any]]:
        self._ensure_connected()
        table = self._resource.Table(table_name)
        response = table.get_item(Key=key)
        return response.get("Item")

    def put_item(self, table_name: str, item: dict) -> dict[str, Any]:
        self._ensure_connected()
        table = self._resource.Table(table_name)
        return table.put_item(Item=item)

    def delete_item(self, table_name: str, key: dict) -> dict[str, Any]:
        self._ensure_connected()
        table = self._resource.Table(table_name)
        return table.delete_item(Key=key)

    def query(self, table_name: str, **kwargs) -> list[dict[str, Any]]:
        self._ensure_connected()
        table = self._resource.Table(table_name)
        response = table.query(**kwargs)
        return response.get("Items", [])

    def scan(self, table_name: str, **kwargs) -> list[dict[str, Any]]:
        self._ensure_connected()
        table = self._resource.Table(table_name)
        response = table.scan(**kwargs)
        return response.get("Items", [])

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("databases", "dynamodb", DynamoDBConnector)
