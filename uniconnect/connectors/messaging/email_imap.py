from __future__ import annotations

import email
from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import imaplib
except ImportError:
    imaplib = None


class IMAPConnector(SyncConnector):
    name = "email_imap"
    description = "IMAP email connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        host = self.config.get("host", "")
        port = int(self.config.get("port", 993))
        user = self.config.get("user", "")
        password = self.config.get("password", "")

        if imaplib is None:
            raise ImportError("imaplib is a built-in module")

        self._client = imaplib.IMAP4_SSL(host, port)
        self._client.login(user, password)
        self._connected = True

    def close(self) -> None:
        if self._client:
            self._client.logout()
        self._client = None
        self._connected = False

    def list_mailboxes(self) -> list[str]:
        self._ensure_connected()
        result, data = self._client.list()
        if result != "OK":
            raise RuntimeError(f"Failed to list mailboxes: {data}")
        mailboxes = []
        for item in data:
            parts = item.decode().split(' "/" ')
            if len(parts) > 1:
                mailboxes.append(parts[-1].strip('"'))
        return mailboxes

    def fetch_messages(self, mailbox: str = "INBOX", limit: int = 10) -> list[dict]:
        self._ensure_connected()
        self._client.select(mailbox)
        result, data = self._client.search(None, "ALL")
        if result != "OK":
            return []

        msg_ids = data[0].split()
        recent = msg_ids[-limit:] if len(msg_ids) > limit else msg_ids
        messages = []

        for msg_id in recent:
            result, data = self._client.fetch(msg_id, "(RFC822)")
            if result != "OK":
                continue
            raw = email.message_from_bytes(data[0][1])
            messages.append({
                "id": msg_id.decode(),
                "subject": raw["subject"],
                "from": raw["from"],
                "date": raw["date"],
            })

        return messages

    def search(self, criteria: str) -> list[str]:
        self._ensure_connected()
        self._client.select("INBOX")
        result, data = self._client.search(None, criteria)
        if result != "OK":
            return []
        return [mid.decode() for mid in data[0].split()]

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("messaging", "email_imap", IMAPConnector)
