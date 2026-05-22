from __future__ import annotations

import functools
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


class CredentialManager:
    def __init__(self, config: Optional[dict] = None):
        self._config = config or {}

    def get(self, key: str, default: Any = None) -> Any:
        value = self._config.get(key)
        if value is not None:
            return value
        env_key = key.upper().replace("-", "_")
        value = os.environ.get(f"UNICONNECT_{env_key}")
        if value is not None:
            return value
        value = os.environ.get(env_key)
        if value is not None:
            return value
        return default

    def resolve(self, mapping: dict[str, str]) -> dict[str, Any]:
        return {k: self.get(v) for k, v in mapping.items()}


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exc = None
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < max_attempts:
                        time.sleep(wait)
                        wait *= backoff
            raise last_exc  # type: ignore
        return wrapper
    return decorator


class ConnectionPool:
    def __init__(self, connector_cls, max_size: int = 10, **factory_kwargs):
        self._connector_cls = connector_cls
        self._max_size = max_size
        self._factory_kwargs = factory_kwargs
        self._pool: list = []
        self._in_use: set = set()

    def acquire(self):
        if self._pool:
            conn = self._pool.pop()
            self._in_use.add(id(conn))
            if not conn.is_connected:
                conn.connect()
            return conn
        if len(self._in_use) < self._max_size:
            conn = self._connector_cls(config=self._factory_kwargs)
            conn.connect()
            self._in_use.add(id(conn))
            return conn
        raise RuntimeError("Connection pool exhausted")

    def release(self, conn) -> None:
        self._in_use.discard(id(conn))
        self._pool.append(conn)

    def close_all(self) -> None:
        for conn in self._pool:
            try:
                conn.close()
            except Exception:
                pass
        self._pool.clear()
        self._in_use.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()
