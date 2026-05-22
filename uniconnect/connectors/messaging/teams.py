from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class TeamsConnector(SyncConnector):
    name = "teams"
    description = "Microsoft Teams connector"

    def connect(self) -> None:
        raise NotImplementedError("Teams connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Teams connector is not implemented yet")


registry.register("messaging", "teams", TeamsConnector)
