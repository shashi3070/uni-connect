from __future__ import annotations

from typing import Any, Callable, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import pika
except ImportError:
    pika = None


class RabbitMQConnector(SyncConnector):
    name = "rabbitmq"
    description = "RabbitMQ"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._connection = None
        self._channel = None

    def connect(self) -> None:
        if pika is None:
            raise ImportError("pika is required. Install with: pip install pika")
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 5672)
        user = self.config.get("user", "guest")
        password = self.config.get("password", "guest")
        virtual_host = self.config.get("virtual_host", "/")

        credentials = pika.PlainCredentials(user, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=credentials,
        )
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._connected = True

    def close(self) -> None:
        if self._channel:
            self._channel.close()
        if self._connection:
            self._connection.close()
        self._channel = None
        self._connection = None
        self._connected = False

    def declare_queue(self, queue: str, **kwargs: Any) -> None:
        self._ensure_connected()
        self._channel.queue_declare(queue=queue, **kwargs)

    def publish(self, queue: str, message: str) -> None:
        self._ensure_connected()
        self._channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=message.encode("utf-8"),
        )

    def consume(self, queue: str, callback: Optional[Callable] = None) -> list[dict[str, Any]]:
        self._ensure_connected()
        messages = []

        def _callback(ch, method, properties, body):
            messages.append({
                "message": body.decode("utf-8"),
                "delivery_tag": method.delivery_tag,
            })
            if callback:
                callback(body.decode("utf-8"))

        self._channel.basic_consume(queue=queue, on_message_callback=_callback, auto_ack=True)
        self._channel.start_consuming()
        return messages

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("streaming", "rabbitmq", RabbitMQConnector)
