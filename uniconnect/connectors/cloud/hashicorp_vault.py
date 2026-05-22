from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import hvac
except ImportError:
    hvac = None


class VaultConnector(SyncConnector):
    name = "vault"
    description = "HashiCorp Vault"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if hvac is None:
            raise ImportError("hvac is required. Install with: pip install hvac")
        url = self.config.get("url", "")
        token = self.config.get("token")
        role_id = self.config.get("role_id")
        secret_id = self.config.get("secret_id")

        self._client = hvac.Client(url=url, token=token)

        if not token and role_id and secret_id:
            self._client.auth.approle.login(role_id=role_id, secret_id=secret_id)

        self._connected = True

    def close(self) -> None:
        self._client = None
        self._connected = False

    def read_secret(self, path: str, mount_point: str = "secret") -> dict[str, Any]:
        self._ensure_connected()
        resp = self._client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=mount_point
        )
        return resp.get("data", {}).get("data", {})

    def write_secret(self, path: str, data: dict[str, Any], mount_point: str = "secret") -> None:
        self._ensure_connected()
        self._client.secrets.kv.v2.create_or_update_secret(
            path=path, secret=data, mount_point=mount_point
        )

    def list_secrets(self, path: str, mount_point: str = "secret") -> list[str]:
        self._ensure_connected()
        resp = self._client.secrets.kv.v2.list_secrets(
            path=path, mount_point=mount_point
        )
        return resp.get("data", {}).get("keys", [])

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("cloud", "vault", VaultConnector)
