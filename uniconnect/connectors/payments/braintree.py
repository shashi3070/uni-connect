from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class BraintreeConnector(SyncConnector):
    name = "braintree"
    description = "Braintree payment connector"

    def connect(self) -> None:
        raise NotImplementedError("Braintree connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Braintree connector is not implemented yet")


registry.register("payments", "braintree", BraintreeConnector)
