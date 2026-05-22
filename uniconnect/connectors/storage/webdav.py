from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class WebDAVConnector(SyncConnector):
    name = "webdav"
    description = "WebDAV storage (skeleton)"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)

    def connect(self) -> None:
        raise NotImplementedError(
            "WebDAVConnector is not yet implemented. "
            "Contributions welcome at https://github.com/anomalyco/uni-connect"
        )

    def close(self) -> None:
        raise NotImplementedError(
            "WebDAVConnector is not yet implemented."
        )

    def list_files(self, prefix: str = "") -> list[str]:
        raise NotImplementedError("WebDAVConnector is not yet implemented.")

    def read_file(self, path: str) -> bytes:
        raise NotImplementedError("WebDAVConnector is not yet implemented.")

    def write_file(self, path: str, data: bytes) -> None:
        raise NotImplementedError("WebDAVConnector is not yet implemented.")

    def delete_file(self, path: str) -> None:
        raise NotImplementedError("WebDAVConnector is not yet implemented.")

    def file_exists(self, path: str) -> bool:
        raise NotImplementedError("WebDAVConnector is not yet implemented.")


registry.register("storage", "webdav", WebDAVConnector)
