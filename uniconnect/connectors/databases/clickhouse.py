from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class ClickHouseConnector(SyncConnector):
    name = "clickhouse"
    description = "ClickHouse column-oriented database connector"

    def connect(self) -> None:
        raise NotImplementedError("ClickHouse connector: install 'clickhouse-driver' package")

    def close(self) -> None:
        pass


registry.register("databases", "clickhouse", ClickHouseConnector)
