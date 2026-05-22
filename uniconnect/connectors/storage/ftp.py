from __future__ import annotations

import io
import os
import tempfile
from ftplib import FTP, FTP_TLS
from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class FTPConnector(SyncConnector):
    name = "ftp"
    description = "FTP and FTPS storage"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._ftp = None

    def connect(self) -> None:
        host = self.config.get("host", "")
        port = int(self.config.get("port", 21))
        user = self.config.get("user", "anonymous")
        password = self.config.get("password", "anonymous@")
        tls = self.config.get("tls", False)

        if tls:
            self._ftp = FTP_TLS()
        else:
            self._ftp = FTP()

        self._ftp.connect(host, port)
        self._ftp.login(user, password)

        if tls:
            self._ftp.prot_p()

        self._connected = True

    def close(self) -> None:
        if self._ftp:
            try:
                self._ftp.quit()
            except Exception:
                self._ftp.close()
        self._ftp = None
        self._connected = False

    def list_files(self, prefix: str = "") -> list[str]:
        self._ensure_connected()
        files = []
        self._ftp.retrlines(f"LIST {prefix}", files.append)
        return files

    def read_file(self, path: str) -> bytes:
        self._ensure_connected()
        buf = io.BytesIO()

        def callback(data: bytes) -> None:
            buf.write(data)

        self._ftp.retrbinary(f"RETR {path}", callback)
        return buf.getvalue()

    def write_file(self, path: str, data: bytes) -> None:
        self._ensure_connected()
        buf = io.BytesIO(data)
        self._ftp.storbinary(f"STOR {path}", buf)

    def delete_file(self, path: str) -> None:
        self._ensure_connected()
        self._ftp.delete(path)

    def file_exists(self, path: str) -> bool:
        self._ensure_connected()
        try:
            self._ftp.size(path)
            return True
        except Exception:
            return False

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("storage", "ftp", FTPConnector)
