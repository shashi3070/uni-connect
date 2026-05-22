from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class PubSubConnector(SyncConnector):
    name = "pubsub"
    description = "Google Cloud Pub/Sub"

    def connect(self) -> None:
        raise NotImplementedError("Pub/Sub connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Pub/Sub connector is not yet implemented")


registry.register("streaming", "pubsub", PubSubConnector)
