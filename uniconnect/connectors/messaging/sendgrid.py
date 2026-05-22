from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import requests
except ImportError:
    requests = None


class SendGridConnector(SyncConnector):
    name = "sendgrid"
    description = "SendGrid email connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._api_key = ""
        self._base_url = "https://api.sendgrid.com/v3"

    def connect(self) -> None:
        self._api_key = self.config.get("api_key", "")
        if not self._api_key:
            raise ValueError("api_key is required for SendGrid connector")
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")
        self._connected = True

    def close(self) -> None:
        self._connected = False

    def send(
        self,
        to: str | list[str],
        subject: str,
        body: str,
        html: Optional[str] = None,
    ) -> dict:
        self._ensure_connected()
        recipients = [to] if isinstance(to, str) else to

        content = [{"type": "text/plain", "value": body}]
        if html:
            content.append({"type": "text/html", "value": html})

        payload = {
            "personalizations": [{"to": [{"email": r} for r in recipients]}],
            "from": {"email": self.config.get("from_email", "")},
            "subject": subject,
            "content": content,
        }

        resp = requests.post(
            f"{self._base_url}/mail/send",
            json=payload,
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
        resp.raise_for_status()
        return {"status": "sent", "to": recipients, "subject": subject}

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("messaging", "sendgrid", SendGridConnector)
