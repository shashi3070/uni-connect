from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import docker as docker_py
except ImportError:
    docker_py = None


class DockerConnector(SyncConnector):
    name = "docker"
    description = "Docker containers"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if docker_py is None:
            raise ImportError("docker is required. Install with: pip install docker")
        base_url = self.config.get("base_url")
        if base_url:
            self._client = docker_py.DockerClient(base_url=base_url)
        else:
            self._client = docker_py.from_env()
        self._connected = True

    def close(self) -> None:
        if self._client:
            self._client.close()
        self._client = None
        self._connected = False

    def list_containers(self, all: bool = False) -> list[dict[str, Any]]:
        self._ensure_connected()
        containers = self._client.containers.list(all=all)
        return [c.attrs for c in containers]

    def run_container(self, image: str, command: Optional[str] = None, **kwargs: Any) -> Any:
        self._ensure_connected()
        return self._client.containers.run(image, command=command, **kwargs)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("cloud", "docker", DockerConnector)
