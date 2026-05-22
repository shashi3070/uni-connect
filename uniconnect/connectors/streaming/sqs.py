from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import boto3
except ImportError:
    boto3 = None


class SQSConnector(SyncConnector):
    name = "sqs"
    description = "Amazon SQS"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None
        self._queue_url = ""

    def connect(self) -> None:
        if boto3 is None:
            raise ImportError("boto3 is required. Install with: pip install boto3")
        self._client = boto3.client(
            "sqs",
            aws_access_key_id=self.config.get("aws_access_key_id"),
            aws_secret_access_key=self.config.get("aws_secret_access_key"),
            region_name=self.config.get("region"),
        )
        self._queue_url = self.config.get("queue_url", "")
        self._connected = True

    def close(self) -> None:
        if self._client:
            self._client.close()
        self._client = None
        self._connected = False

    def send(self, message: str) -> dict[str, Any]:
        self._ensure_connected()
        return self._client.send_message(QueueUrl=self._queue_url, MessageBody=message)

    def receive(self, max_messages: int = 1, wait_time: int = 2) -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._client.receive_message(
            QueueUrl=self._queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time,
        )
        return resp.get("Messages", [])

    def delete(self, receipt_handle: str) -> dict[str, Any]:
        self._ensure_connected()
        return self._client.delete_message(
            QueueUrl=self._queue_url,
            ReceiptHandle=receipt_handle,
        )

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("streaming", "sqs", SQSConnector)
