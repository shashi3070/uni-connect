from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    from google.cloud import pubsub_v1
except ImportError:
    pubsub_v1 = None

try:
    import googleapiclient.discovery
except ImportError:
    googleapiclient = None


class GCPConnector(SyncConnector):
    name = "gcp"
    description = "Google Cloud Platform"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._clients: dict[str, Any] = {}
        self._credentials = None

    def connect(self) -> None:
        credentials_path = self.config.get("credentials_path")
        if credentials_path:
            try:
                from google.oauth2 import service_account
            except ImportError:
                raise ImportError("google-auth is required. Install with: pip install google-auth")
            self._credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
        self._connected = True

    def close(self) -> None:
        self._clients.clear()
        self._credentials = None
        self._connected = False

    def get_client(self, service: str, version: str = "v1") -> Any:
        self._ensure_connected()
        if service not in self._clients:
            if googleapiclient is None:
                raise ImportError("google-api-python-client is required. Install with: pip install google-api-python-client")
            self._clients[service] = googleapiclient.discovery.build(
                service, version, credentials=self._credentials
            )
        return self._clients[service]

    def list_pubsub_topics(self, project: Optional[str] = None) -> list[str]:
        self._ensure_connected()
        if pubsub_v1 is None:
            raise ImportError("google-cloud-pubsub is required. Install with: pip install google-cloud-pubsub")
        project = project or self.config.get("project", "")
        if not project:
            raise ValueError("project is required")
        publisher = pubsub_v1.PublisherClient(credentials=self._credentials)
        parent = f"projects/{project}"
        topics = []
        for topic in publisher.list_topics(request={"parent": parent}):
            topics.append(topic.name)
        return topics

    def publish_pubsub(self, topic: str, data: str, project: Optional[str] = None) -> str:
        self._ensure_connected()
        if pubsub_v1 is None:
            raise ImportError("google-cloud-pubsub is required. Install with: pip install google-cloud-pubsub")
        project = project or self.config.get("project", "")
        if not project:
            raise ValueError("project is required")
        publisher = pubsub_v1.PublisherClient(credentials=self._credentials)
        topic_path = publisher.topic_path(project, topic)
        future = publisher.publish(topic_path, data.encode("utf-8"))
        return future.result()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("cloud", "gcp", GCPConnector)
