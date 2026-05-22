from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class ShopifyConnector(SyncConnector):
    name = "shopify"
    description = "Shopify payment connector"

    def connect(self) -> None:
        raise NotImplementedError("Shopify connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Shopify connector is not implemented yet")


registry.register("payments", "shopify", ShopifyConnector)
