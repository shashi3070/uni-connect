from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class ZeroMQConnector(SyncConnector):
    name = "zmq"
    description = "ZeroMQ messaging"

    def connect(self) -> None:
        raise NotImplementedError("ZeroMQ connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("ZeroMQ connector is not yet implemented")


registry.register("streaming", "zmq", ZeroMQConnector)
