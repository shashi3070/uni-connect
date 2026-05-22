from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class TelegramConnector(SyncConnector):
    name = "telegram"
    description = "Telegram messaging connector"

    def connect(self) -> None:
        raise NotImplementedError("Telegram connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Telegram connector is not implemented yet")


registry.register("messaging", "telegram", TelegramConnector)
