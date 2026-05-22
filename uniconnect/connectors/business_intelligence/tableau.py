from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class TableauConnector(SyncConnector):
    name = "tableau"
    description = "Tableau"

    def connect(self) -> None:
        raise NotImplementedError("Tableau connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Tableau connector is not yet implemented")


registry.register("business_intelligence", "tableau", TableauConnector)
