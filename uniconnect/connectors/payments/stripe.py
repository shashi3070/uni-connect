from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import stripe as stripe_lib
except ImportError:
    stripe_lib = None


class StripeConnector(SyncConnector):
    name = "stripe"
    description = "Stripe payment connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._api_key = ""

    def connect(self) -> None:
        self._api_key = self.config.get("api_key", "")
        if not self._api_key:
            raise ValueError("api_key is required for Stripe connector")
        if stripe_lib is None:
            raise ImportError("stripe is required. Install with: pip install stripe")
        stripe_lib.api_key = self._api_key
        self._connected = True

    def close(self) -> None:
        self._connected = False

    def list_products(self) -> list[dict]:
        self._ensure_connected()
        products = stripe_lib.Product.list()
        return [p.to_dict() for p in products.auto_paging_iter()]

    def list_customers(self) -> list[dict]:
        self._ensure_connected()
        customers = stripe_lib.Customer.list()
        return [c.to_dict() for c in customers.auto_paging_iter()]

    def create_payment_intent(self, amount: int, currency: str = "usd") -> dict:
        self._ensure_connected()
        intent = stripe_lib.PaymentIntent.create(amount=amount, currency=currency)
        return intent.to_dict()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("payments", "stripe", StripeConnector)
