from __future__ import annotations

import json
from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import boto3
except ImportError:
    boto3 = None


class BedrockConnector(SyncConnector):
    name = "bedrock"
    description = "AWS Bedrock connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if boto3 is None:
            raise ImportError("boto3 is required. Install with: pip install boto3")

        self._client = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=self.config.get("aws_access_key_id"),
            aws_secret_access_key=self.config.get("aws_secret_access_key"),
            region_name=self.config.get("region", "us-east-1"),
        )
        self._connected = True

    def close(self) -> None:
        self._client = None
        self._connected = False

    def _get_model_id(self) -> str:
        return self.config.get("model_id", "anthropic.claude-v2")

    def complete(self, messages: list[dict], **kwargs: Any) -> dict:
        self._ensure_connected()
        model_id = self._get_model_id()
        body = {
            "messages": messages,
            **kwargs,
        }
        resp = self._client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        return json.loads(resp["body"].read())

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("ai", "bedrock", BedrockConnector)
