from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class DiscordConnector(SyncConnector):
    name = "discord"
    description = "Discord messaging connector"

    def connect(self) -> None:
        raise NotImplementedError("Discord connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Discord connector is not implemented yet")


registry.register("messaging", "discord", DiscordConnector)
