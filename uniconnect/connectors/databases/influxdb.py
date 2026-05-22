from __future__ import annotations

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry


class InfluxDBConnector(SyncConnector):
    name = "influxdb"
    description = "InfluxDB time-series database connector"

    def connect(self) -> None:
        raise NotImplementedError("InfluxDB connector: install 'influxdb-client' package")

    def close(self) -> None:
        pass


registry.register("databases", "influxdb", InfluxDBConnector)
