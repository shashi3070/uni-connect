from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class LocalConnector(SyncConnector):
    name = "local"
    description = "Local filesystem storage"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.base_path: Optional[Path] = None

    def connect(self) -> None:
        base_path = self.config.get("base_path", "")
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._connected = True

    def close(self) -> None:
        self.base_path = None
        self._connected = False

    def _resolve(self, path: str) -> Path:
        resolved = (self.base_path / path).resolve()
        if not str(resolved).startswith(str(self.base_path)):
            raise PermissionError(f"Path traversal detected: {path}")
        return resolved

    def list_files(self, prefix: str = "") -> list[str]:
        self._ensure_connected()
        target = (self.base_path / prefix).resolve() if prefix else self.base_path
        if not target.exists():
            return []
        return [
            str(f.relative_to(self.base_path))
            for f in target.rglob("*")
            if f.is_file()
        ]

    def read_file(self, path: str) -> bytes:
        self._ensure_connected()
        full_path = self._resolve(path)
        return full_path.read_bytes()

    def write_file(self, path: str, data: bytes) -> None:
        self._ensure_connected()
        full_path = self._resolve(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(data)

    def delete_file(self, path: str) -> None:
        self._ensure_connected()
        full_path = self._resolve(path)
        if full_path.exists():
            full_path.unlink()

    def file_exists(self, path: str) -> bool:
        self._ensure_connected()
        full_path = self._resolve(path)
        return full_path.exists()

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("storage", "local", LocalConnector)
