from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class LinearConnector(SyncConnector):
    name = "linear"
    description = "Linear"

    def connect(self) -> None:
        raise NotImplementedError("Linear connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Linear connector is not yet implemented")


registry.register("collaboration", "linear", LinearConnector)
