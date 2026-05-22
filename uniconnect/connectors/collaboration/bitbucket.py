from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class BitbucketConnector(SyncConnector):
    name = "bitbucket"
    description = "Bitbucket"

    def connect(self) -> None:
        raise NotImplementedError("Bitbucket connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("Bitbucket connector is not yet implemented")


registry.register("collaboration", "bitbucket", BitbucketConnector)
