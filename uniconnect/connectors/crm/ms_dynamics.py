from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class MSDynamicsConnector(SyncConnector):
    name = "ms_dynamics"
    description = "Microsoft Dynamics 365 CRM connector"

    def connect(self) -> None:
        raise NotImplementedError("MS Dynamics connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("MS Dynamics connector is not implemented yet")


registry.register("crm", "ms_dynamics", MSDynamicsConnector)
