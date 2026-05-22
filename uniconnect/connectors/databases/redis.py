from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import redis as redis_lib
except ImportError:
    redis_lib = None


class RedisConnector(SyncConnector):
    name = "redis"
    description = "Redis database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if redis_lib is None:
            raise ImportError("redis is required. Install with: pip install redis")

        host = self.config.get("host", "localhost")
        port = self.config.get("port", 6379)
        password = self.config.get("password", None)
        db = self.config.get("db", 0)

        self._client = redis_lib.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True,
        )
        self._client.ping()
        self._connected = True

    def close(self) -> None:
        if self._client:
            self._client.close()
        self._client = None
        self._connected = False

    def get(self, key: str) -> Optional[str]:
        self._ensure_connected()
        return self._client.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._ensure_connected()
        return self._client.set(key, value, ex=ex)

    def delete(self, key: str) -> bool:
        self._ensure_connected()
        return bool(self._client.delete(key))

    def exists(self, key: str) -> bool:
        self._ensure_connected()
        return bool(self._client.exists(key))

    def publish(self, channel: str, message: str) -> int:
        self._ensure_connected()
        return self._client.publish(channel, message)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("databases", "redis", RedisConnector)
