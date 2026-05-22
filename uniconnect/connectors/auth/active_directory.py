from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class ActiveDirectoryConnector(SyncConnector):
    name = "active_directory"
    description = "Microsoft Active Directory"

    def connect(self) -> None:
        raise NotImplementedError("Active Directory connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Active Directory connector is not yet implemented")


registry.register("auth", "active_directory", ActiveDirectoryConnector)
