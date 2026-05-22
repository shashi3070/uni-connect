from __future__ import annotations

import email.mime.application
import email.mime.base
import email.mime.multipart
import email.mime.text
import smtplib
import ssl
from email.utils import formataddr
from typing import Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class SMTPConnector(SyncConnector):
    name = "email_smtp"
    description = "SMTP email connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._server: Optional[smtplib.SMTP] = None

    def connect(self) -> None:
        host = self.config.get("host", "")
        port = int(self.config.get("port", 587))
        user = self.config.get("user", "")
        password = self.config.get("password", "")
        use_tls = self.config.get("use_tls", True)

        if use_tls:
            context = ssl.create_default_context()
            self._server = smtplib.SMTP(host, port)
            self._server.starttls(context=context)
        else:
            self._server = smtplib.SMTP_SSL(host, port)

        if user and password:
            self._server.login(user, password)

        self._connected = True

    def close(self) -> None:
        if self._server:
            self._server.quit()
        self._server = None
        self._connected = False

    def send(
        self,
        to: str | list[str],
        subject: str,
        body: str,
        html: Optional[str] = None,
        attachments: Optional[list[dict]] = None,
    ) -> dict:
        self._ensure_connected()

        recipients = [to] if isinstance(to, str) else to
        from_addr = self.config.get("user", "")

        if html or attachments:
            msg = email.mime.multipart.MIMEMultipart("alternative")
        else:
            msg = email.mime.text.MIMEText(body, "plain")

        msg["Subject"] = subject
        msg["From"] = formataddr((self.config.get("from_name", ""), from_addr))
        msg["To"] = ", ".join(recipients)

        if html:
            part1 = email.mime.text.MIMEText(body, "plain")
            part2 = email.mime.text.MIMEText(html, "html")
            msg.attach(part1)
            msg.attach(part2)

        if attachments:
            for attachment in attachments or []:
                file_path = attachment.get("path")
                filename = attachment.get("filename")
                if file_path:
                    with open(file_path, "rb") as f:
                        part = email.mime.base.MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    email.encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={filename or file_path}",
                    )
                    msg.attach(part)

        self._server.sendmail(from_addr, recipients, msg.as_string())

        return {"status": "sent", "to": recipients, "subject": subject}

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("messaging", "email_smtp", SMTPConnector)
