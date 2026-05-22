from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class LDAPConnector(SyncConnector):
    name = "ldap"
    description = "LDAP authentication"

    def connect(self) -> None:
        raise NotImplementedError("LDAP connector is not yet implemented")

    def close(self) -> None:
        raise NotImplementedError("LDAP connector is not yet implemented")


registry.register("auth", "ldap", LDAPConnector)
