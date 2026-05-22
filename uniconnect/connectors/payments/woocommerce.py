from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class WooCommerceConnector(SyncConnector):
    name = "woocommerce"
    description = "WooCommerce payment connector"

    def connect(self) -> None:
        raise NotImplementedError("WooCommerce connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("WooCommerce connector is not implemented yet")


registry.register("payments", "woocommerce", WooCommerceConnector)
