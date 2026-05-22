from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import kubernetes as k8s
except ImportError:
    k8s = None


class KubernetesConnector(SyncConnector):
    name = "kubernetes"
    description = "Kubernetes container orchestration"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._core = None
        self._apps = None

    def connect(self) -> None:
        if k8s is None:
            raise ImportError("kubernetes is required. Install with: pip install kubernetes")
        k8s.config.load_kube_config()
        self._core = k8s.client.CoreV1Api()
        self._apps = k8s.client.AppsV1Api()
        self._connected = True

    def close(self) -> None:
        self._core = None
        self._apps = None
        self._connected = False

    def list_pods(self, namespace: str = "default") -> list[dict[str, Any]]:
        self._ensure_connected()
        resp = self._core.list_namespaced_pod(namespace)
        return [pod.to_dict() for pod in resp.items]

    def get_logs(self, name: str, namespace: str = "default") -> str:
        self._ensure_connected()
        return self._core.read_namespaced_pod_log(name=name, namespace=namespace)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("cloud", "kubernetes", KubernetesConnector)
