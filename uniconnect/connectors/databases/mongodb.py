from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    import pymongo
except ImportError:
    pymongo = None

try:
    import motor
except ImportError:
    motor = None


class MongoDBConnector(SyncConnector):
    name = "mongodb"
    description = "MongoDB database connector"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None
        self._db = None

    def connect(self) -> None:
        driver = self.config.get("driver", "pymongo")
        uri = self.config.get("uri", "mongodb://localhost:27017")
        database = self.config.get("database", "")

        if driver == "pymongo":
            if pymongo is None:
                raise ImportError("pymongo is required. Install with: pip install pymongo")
            self._client = pymongo.MongoClient(uri)
            self._db = self._client[database] if database else None
        elif driver == "motor":
            if motor is None:
                raise ImportError("motor is required. Install with: pip install motor")
            raise RuntimeError(
                "motor is an async driver. Use AsyncMongoDBConnector instead."
            )
        else:
            raise ValueError(f"Unsupported driver: {driver}")

        self._connected = True

    def close(self) -> None:
        if self._client:
            self._client.close()
        self._client = None
        self._db = None
        self._connected = False

    @property
    def _collection(self):
        collection_name = self.config.get("collection", "")
        if self._db is None:
            raise ConnectionError("Database not specified in config")
        return self._db[collection_name]

    def find(self, filter: Optional[dict] = None, **kwargs) -> list[dict[str, Any]]:
        self._ensure_connected()
        return list(self._collection.find(filter or {}, **kwargs))

    def find_one(self, filter: Optional[dict] = None, **kwargs) -> Optional[dict[str, Any]]:
        self._ensure_connected()
        return self._collection.find_one(filter or {}, **kwargs)

    def insert_one(self, document: dict) -> Any:
        self._ensure_connected()
        return self._collection.insert_one(document)

    def insert_many(self, documents: list[dict]) -> Any:
        self._ensure_connected()
        return self._collection.insert_many(documents)

    def update_one(self, filter: dict, update: dict, **kwargs) -> Any:
        self._ensure_connected()
        return self._collection.update_one(filter, update, **kwargs)

    def delete_one(self, filter: dict) -> Any:
        self._ensure_connected()
        return self._collection.delete_one(filter)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("databases", "mongodb", MongoDBConnector)
registry.register("databases", "mongodb", MongoDBConnector, driver="pymongo")
registry.register("databases", "mongodb", MongoDBConnector, driver="motor")
