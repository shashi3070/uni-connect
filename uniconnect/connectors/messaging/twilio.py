from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    from twilio.rest import Client
except ImportError:
    Client = None


class TwilioConnector(SyncConnector):
    name = "twilio"
    description = "Twilio SMS and WhatsApp connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        account_sid = self.config.get("account_sid", "")
        auth_token = self.config.get("auth_token", "")
        if not account_sid or not auth_token:
            raise ValueError("account_sid and auth_token are required for Twilio connector")
        if Client is None:
            raise ImportError("twilio is required. Install with: pip install twilio")
        self._client = Client(account_sid, auth_token)
        self._from_number = self.config.get("from_number", "")
        self._connected = True

    def close(self) -> None:
        self._client = None
        self._connected = False

    def send_sms(self, to: str, body: str) -> dict:
        self._ensure_connected()
        message = self._client.messages.create(
            to=to,
            from_=self._from_number,
            body=body,
        )
        return {"sid": message.sid, "status": message.status}

    def send_whatsapp(self, to: str, body: str) -> dict:
        self._ensure_connected()
        message = self._client.messages.create(
            to=f"whatsapp:{to}",
            from_=f"whatsapp:{self._from_number}",
            body=body,
        )
        return {"sid": message.sid, "status": message.status}

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("messaging", "twilio", TwilioConnector)
