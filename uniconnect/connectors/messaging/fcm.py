from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class FCMConnector(SyncConnector):
    name = "fcm"
    description = "Firebase Cloud Messaging connector"

    def connect(self) -> None:
        raise NotImplementedError("FCM connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("FCM connector is not implemented yet")


registry.register("messaging", "fcm", FCMConnector)
