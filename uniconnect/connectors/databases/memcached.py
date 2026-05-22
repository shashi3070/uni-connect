from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class MemcachedConnector(SyncConnector):
    name = "memcached"
    description = "Memcached database connector"

    def connect(self) -> None:
        raise NotImplementedError("Memcached connector: install 'pymemcache' package")

    def close(self) -> None:
        pass


registry.register("databases", "memcached", MemcachedConnector)
