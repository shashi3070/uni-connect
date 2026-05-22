from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    from kafka import KafkaProducer, KafkaConsumer
except ImportError:
    KafkaProducer = None
    KafkaConsumer = None


class KafkaConnector(SyncConnector):
    name = "kafka"
    description = "Apache Kafka"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._producer = None
        self._consumer = None

    def connect(self) -> None:
        if KafkaProducer is None:
            raise ImportError("kafka-python is required. Install with: pip install kafka-python")
        bootstrap_servers = self.config.get("bootstrap_servers", "localhost:9092")
        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            value_serializer=lambda v: v.encode("utf-8") if isinstance(v, str) else v,
        )
        self._connected = True

    def close(self) -> None:
        if self._producer:
            self._producer.close()
        if self._consumer:
            self._consumer.close()
        self._producer = None
        self._consumer = None
        self._connected = False

    def produce(self, topic: str, value: str, key: Optional[str] = None) -> None:
        self._ensure_connected()
        self._producer.send(topic, value=value, key=key)
        self._producer.flush()

    def consume(self, topic: str, timeout: float = 1.0) -> list[dict[str, Any]]:
        self._ensure_connected()
        if KafkaConsumer is None:
            raise ImportError("kafka-python is required. Install with: pip install kafka-python")
        bootstrap_servers = self.config.get("bootstrap_servers", "localhost:9092")
        group_id = self.config.get("group_id")
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            consumer_timeout_ms=int(timeout * 1000),
            value_deserializer=lambda v: v.decode("utf-8"),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
        )
        messages = []
        for msg in consumer:
            messages.append({
                "key": msg.key,
                "value": msg.value,
                "partition": msg.partition,
                "offset": msg.offset,
            })
        consumer.close()
        return messages

    def list_topics(self) -> list[str]:
        self._ensure_connected()
        topics = self._producer.list_topics()
        return list(topics)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("streaming", "kafka", KafkaConnector)
