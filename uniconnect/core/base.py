from __future__ import annotations

import abc
from typing import Any, Optional


class BaseConnector(abc.ABC):
    name: str = ""
    description: str = ""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self._connected = False

    @abc.abstractmethod
    def connect(self) -> None:
        ...

    @abc.abstractmethod
    def close(self) -> None:
        ...

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def is_connected(self) -> bool:
        return self._connected

    def health_check(self) -> bool:
        return self._connected


class SyncConnector(BaseConnector):
    @abc.abstractmethod
    def connect(self) -> None:
        ...

    @abc.abstractmethod
    def close(self) -> None:
        ...


class AsyncConnector(BaseConnector):
    @abc.abstractmethod
    async def connect(self) -> None:
        ...

    @abc.abstractmethod
    async def close(self) -> None:
        ...

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
