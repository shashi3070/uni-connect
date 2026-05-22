from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class PushbulletConnector(SyncConnector):
    name = "pushbullet"
    description = "Pushbullet notification connector"

    def connect(self) -> None:
        raise NotImplementedError("Pushbullet connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Pushbullet connector is not implemented yet")


registry.register("messaging", "pushbullet", PushbulletConnector)
