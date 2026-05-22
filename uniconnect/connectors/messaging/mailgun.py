from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import requests
except ImportError:
    requests = None


class MailgunConnector(SyncConnector):
    name = "mailgun"
    description = "Mailgun email connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._api_key = ""
        self._domain = ""

    def connect(self) -> None:
        self._api_key = self.config.get("api_key", "")
        self._domain = self.config.get("domain", "")
        if not self._api_key or not self._domain:
            raise ValueError("api_key and domain are required for Mailgun connector")
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")
        self._connected = True

    def close(self) -> None:
        self._connected = False

    def send(self, to: str | list[str], subject: str, body: str) -> dict:
        self._ensure_connected()
        recipients = [to] if isinstance(to, str) else to

        resp = requests.post(
            f"https://api.mailgun.net/v3/{self._domain}/messages",
            auth=("api", self._api_key),
            data={
                "from": self.config.get("from_email", f"noreply@{self._domain}"),
                "to": recipients,
                "subject": subject,
                "text": body,
            },
        )
        resp.raise_for_status()
        return {"status": "sent", "to": recipients, "subject": subject, "id": resp.json().get("id")}

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("messaging", "mailgun", MailgunConnector)
