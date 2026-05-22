from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class GitLabConnector(SyncConnector):
    name = "gitlab"
    description = "GitLab"

    def connect(self) -> None:
        raise NotImplementedError("GitLab connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("GitLab connector is not yet implemented")


registry.register("collaboration", "gitlab", GitLabConnector)
