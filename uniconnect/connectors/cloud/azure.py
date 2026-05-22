from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    from azure.identity import ClientSecretCredential, DefaultAzureCredential
except ImportError:
    ClientSecretCredential = None
    DefaultAzureCredential = None

try:
    from azure.mgmt.resource import ResourceManagementClient
except ImportError:
    ResourceManagementClient = None


class AzureConnector(SyncConnector):
    name = "azure"
    description = "Microsoft Azure"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._credential = None
        self._clients: dict[str, Any] = {}

    def connect(self) -> None:
        tenant_id = self.config.get("tenant_id")
        client_id = self.config.get("client_id")
        client_secret = self.config.get("client_secret")

        if client_id and client_secret and tenant_id:
            if ClientSecretCredential is None:
                raise ImportError("azure-identity is required. Install with: pip install azure-identity")
            self._credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        elif tenant_id:
            if DefaultAzureCredential is None:
                raise ImportError("azure-identity is required. Install with: pip install azure-identity")
            self._credential = DefaultAzureCredential()
        else:
            if DefaultAzureCredential is None:
                raise ImportError("azure-identity is required. Install with: pip install azure-identity")
            self._credential = DefaultAzureCredential()

        self._connected = True

    def close(self) -> None:
        self._clients.clear()
        self._credential = None
        self._connected = False

    def get_client(self, service: str) -> Any:
        self._ensure_connected()
        if service not in self._clients:
            subscription_id = self.config.get("subscription_id", "")
            if service == "resource":
                if ResourceManagementClient is None:
                    raise ImportError("azure-mgmt-resource is required. Install with: pip install azure-mgmt-resource")
                self._clients[service] = ResourceManagementClient(
                    self._credential, subscription_id
                )
            else:
                raise ValueError(f"Unsupported Azure service: {service}")
        return self._clients[service]

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("cloud", "azure", AzureConnector)
