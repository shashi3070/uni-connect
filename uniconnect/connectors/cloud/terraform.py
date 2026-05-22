from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class TerraformConnector(SyncConnector):
    name = "terraform"
    description = "HashiCorp Terraform"

    def connect(self) -> None:
        raise NotImplementedError("Terraform connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Terraform connector is not yet implemented")


registry.register("cloud", "terraform", TerraformConnector)
