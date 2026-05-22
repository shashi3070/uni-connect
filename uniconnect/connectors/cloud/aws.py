from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import boto3
except ImportError:
    boto3 = None


class AWSConnector(SyncConnector):
    name = "aws"
    description = "Amazon Web Services"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._session = None
        self._clients: dict[str, Any] = {}

    def connect(self) -> None:
        if boto3 is None:
            raise ImportError("boto3 is required. Install with: pip install boto3")
        self._session = boto3.Session(
            aws_access_key_id=self.config.get("aws_access_key_id"),
            aws_secret_access_key=self.config.get("aws_secret_access_key"),
            region_name=self.config.get("region"),
        )
        self._connected = True

    def close(self) -> None:
        self._clients.clear()
        self._session = None
        self._connected = False

    def get_client(self, service: str) -> Any:
        self._ensure_connected()
        if service not in self._clients:
            self._clients[service] = self._session.client(service)
        return self._clients[service]

    def list_s3_buckets(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        s3 = self.get_client("s3")
        resp = s3.list_buckets()
        return resp.get("Buckets", [])

    def list_lambda_functions(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        lam = self.get_client("lambda")
        functions = []
        paginator = lam.get_paginator("list_functions")
        for page in paginator.paginate():
            functions.extend(page.get("Functions", []))
        return functions

    def list_sqs_queues(self) -> list[str]:
        self._ensure_connected()
        sqs = self.get_client("sqs")
        resp = sqs.list_queues()
        return resp.get("QueueUrls", [])

    def send_sqs_message(self, queue_url: str, message: str) -> dict[str, Any]:
        self._ensure_connected()
        sqs = self.get_client("sqs")
        return sqs.send_message(QueueUrl=queue_url, MessageBody=message)

    def invoke_lambda(self, function_name: str, payload: str) -> dict[str, Any]:
        self._ensure_connected()
        lam = self.get_client("lambda")
        return lam.invoke(FunctionName=function_name, Payload=payload)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("cloud", "aws", AWSConnector)
