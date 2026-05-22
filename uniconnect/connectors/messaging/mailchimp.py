from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class MailchimpConnector(SyncConnector):
    name = "mailchimp"
    description = "Mailchimp email connector"

    def connect(self) -> None:
        raise NotImplementedError("Mailchimp connector is not implemented yet")

    def close(self) -> None:
        raise NotImplementedError("Mailchimp connector is not implemented yet")


registry.register("messaging", "mailchimp", MailchimpConnector)
