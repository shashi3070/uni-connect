from __future__ import annotations

import io
from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import paramiko
except ImportError:
    paramiko = None

try:
    import pysftp
except ImportError:
    pysftp = None

try:
    import asyncssh
except ImportError:
    asyncssh = None


class SFTPConnector(SyncConnector):
    name = "sftp"
    description = "SFTP storage supporting paramiko, pysftp, and asyncssh"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None
        self._sftp = None

    def connect(self) -> None:
        driver = self.config.get("driver", "paramiko")
        host = self.config.get("host", "")
        port = int(self.config.get("port", 22))
        user = self.config.get("user", "")
        password = self.config.get("password")
        private_key_path = self.config.get("private_key_path")

        if driver == "paramiko":
            if paramiko is None:
                raise ImportError(
                    "paramiko is required. Install with: pip install paramiko"
                )
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            connect_kwargs: dict[str, Any] = {
                "hostname": host,
                "port": port,
                "username": user,
            }
            if private_key_path:
                connect_kwargs["key_filename"] = private_key_path
            if password:
                connect_kwargs["password"] = password

            self._client.connect(**connect_kwargs)
            self._sftp = self._client.open_sftp()

        elif driver == "pysftp":
            if pysftp is None:
                raise ImportError(
                    "pysftp is required. Install with: pip install pysftp"
                )
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            connect_kwargs = {
                "host": host,
                "port": port,
                "username": user,
            }
            if private_key_path:
                connect_kwargs["private_key"] = private_key_path
            if password:
                connect_kwargs["password"] = password

            self._sftp = pysftp.Connection(**connect_kwargs, cnopts=cnopts)

        elif driver == "asyncssh":
            if asyncssh is None:
                raise ImportError(
                    "asyncssh is required. Install with: pip install asyncssh"
                )
            raise NotImplementedError(
                "asyncssh driver is async-only; use an async connector instead."
            )
        else:
            raise ValueError(f"Unsupported driver: {driver}")

        self._connected = True

    def close(self) -> None:
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
        self._sftp = None
        self._client = None
        self._connected = False

    def list_files(self, prefix: str = "") -> list[str]:
        self._ensure_connected()
        return self._sftp.listdir(prefix) if prefix else self._sftp.listdir()

    def read_file(self, path: str) -> bytes:
        self._ensure_connected()
        with self._sftp.open(path, "rb") as f:
            return f.read()

    def write_file(self, path: str, data: bytes) -> None:
        self._ensure_connected()
        with self._sftp.open(path, "wb") as f:
            f.write(data)

    def delete_file(self, path: str) -> None:
        self._ensure_connected()
        self._sftp.remove(path)

    def file_exists(self, path: str) -> bool:
        self._ensure_connected()
        try:
            self._sftp.stat(path)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("storage", "sftp", SFTPConnector)
registry.register("storage", "sftp", SFTPConnector, driver="paramiko")
registry.register("storage", "sftp", SFTPConnector, driver="pysftp")
