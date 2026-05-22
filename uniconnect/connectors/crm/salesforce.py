from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry

try:
    from simple_salesforce import Salesforce as SimpleSalesforce
except ImportError:
    SimpleSalesforce = None

try:
    from pysfdc import Salesforce as PySFDC
except ImportError:
    PySFDC = None


class SalesforceConnector(SyncConnector):
    name = "salesforce"
    description = "Salesforce CRM connector supporting simple-salesforce and PySFDC"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None
        self._driver = None

    def connect(self) -> None:
        self._driver = self.config.get("driver", "simple_salesforce")
        username = self.config.get("username", "")
        password = self.config.get("password", "")
        security_token = self.config.get("security_token", "")
        domain = self.config.get("domain", "login")

        if self._driver == "simple_salesforce":
            if SimpleSalesforce is None:
                raise ImportError("simple-salesforce is required. Install with: pip install simple-salesforce")
            self._client = SimpleSalesforce(
                username=username,
                password=password,
                security_token=security_token,
                domain=domain,
            )
        elif self._driver == "pysfdc":
            if PySFDC is None:
                raise ImportError("PySFDC is required. Install with: pip install PySFDC")
            self._client = PySFDC(
                username=username,
                password=password,
                security_token=security_token,
                is_sandbox=(domain == "test"),
            )
        else:
            raise ValueError(f"Unsupported driver: {self._driver}")

        self._connected = True

    def close(self) -> None:
        self._client = None
        self._connected = False

    def query(self, soql: str) -> Any:
        self._ensure_connected()
        if self._driver == "simple_salesforce":
            return self._client.query_all(soql)
        return self._client.query(soql)

    def describe(self, obj_type: str) -> Any:
        self._ensure_connected()
        if self._driver == "simple_salesforce":
            return getattr(self._client, obj_type).describe()
        return self._client.describe(obj_type)

    def create(self, obj_type: str, data: dict) -> Any:
        self._ensure_connected()
        if self._driver == "simple_salesforce":
            return getattr(self._client, obj_type).create(data)
        return self._client.create(obj_type, data)

    def update(self, obj_type: str, record_id: str, data: dict) -> Any:
        self._ensure_connected()
        if self._driver == "simple_salesforce":
            return getattr(self._client, obj_type).update(record_id, data)
        return self._client.update(obj_type, record_id, data)

    def delete(self, obj_type: str, record_id: str) -> Any:
        self._ensure_connected()
        if self._driver == "simple_salesforce":
            return getattr(self._client, obj_type).delete(record_id)
        return self._client.delete(obj_type, record_id)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("crm", "salesforce", SalesforceConnector)
registry.register("crm", "salesforce", SalesforceConnector, driver="simple_salesforce")
registry.register("crm", "salesforce", SalesforceConnector, driver="pysfdc")
