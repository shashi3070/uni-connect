from __future__ import annotations

import time
from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import boto3
except ImportError:
    boto3 = None


class AthenaConnector(SyncConnector):
    name = "athena"
    description = "Amazon Athena serverless query service"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if boto3 is None:
            raise ImportError("boto3 is required. Install with: pip install boto3")

        self._client = boto3.client(
            "athena",
            aws_access_key_id=self.config.get("aws_access_key_id"),
            aws_secret_access_key=self.config.get("aws_secret_access_key"),
            region_name=self.config.get("region", "us-east-1"),
        )
        self._connected = True

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
        self._connected = False

    def query(self, sql: str) -> list[dict[str, Any]]:
        self._ensure_connected()
        database = self.config.get("database", "default")
        s3_output = self.config.get("s3_output_location", "")

        response = self._client.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={"Database": database},
            ResultConfiguration={"OutputLocation": s3_output},
        )

        query_execution_id = response["QueryExecutionId"]
        self._wait_for_query(query_execution_id)

        result = self._client.get_query_results(QueryExecutionId=query_execution_id)
        rows = result.get("ResultSet", {}).get("Rows", [])
        if not rows:
            return []

        columns = [col.get("Name", "") for col in rows[0].get("Data", [])]
        data = []
        for row in rows[1:]:
            values = [item.get("VarCharValue", "") for item in row.get("Data", [])]
            data.append(dict(zip(columns, values)))

        return data

    def _wait_for_query(self, query_execution_id: str, poll_interval: float = 1.0) -> None:
        while True:
            response = self._client.get_query_execution(QueryExecutionId=query_execution_id)
            state = response["QueryExecution"]["Status"]["State"]
            if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
                if state != "SUCCEEDED":
                    reason = response["QueryExecution"]["Status"].get("StateChangeReason", "Unknown")
                    raise RuntimeError(f"Query {state}: {reason}")
                return
            time.sleep(poll_interval)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("warehouse", "athena", AthenaConnector)
