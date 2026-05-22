from __future__ import annotations

from typing import Any, Optional, Type

from uniconnect.core.base import BaseConnector
from uniconnect.core.exceptions import DriverNotFoundError, NotSupportedError


class Registry:
    def __init__(self):
        self._connectors: dict[str, dict[str, Type[BaseConnector]]] = {}

    def register(
        self,
        category: str,
        name: str,
        connector_cls: Type[BaseConnector],
        driver: Optional[str] = None,
    ) -> None:
        if category not in self._connectors:
            self._connectors[category] = {}
        key = driver if driver else name
        self._connectors[category][key] = connector_cls

    def get(
        self,
        category: str,
        name: str,
        driver: Optional[str] = None,
    ) -> Type[BaseConnector]:
        cat = self._connectors.get(category)
        if not cat:
            raise NotSupportedError(f"Category '{category}' is not registered")
        if driver:
            cls = cat.get(driver)
            if cls:
                return cls
            raise DriverNotFoundError(
                f"Driver '{driver}' not found for '{category}/{name}'"
            )
        cls = cat.get(name)
        if cls:
            return cls
        suggestions = [k for k in cat if k != name]
        msg = (
            f"Connector '{name}' not found in category '{category}'"
        )
        if suggestions:
            msg += f". Available: {', '.join(suggestions)}"
        raise NotSupportedError(msg)

    def list_connectors(self) -> dict[str, list[str]]:
        return {
            cat: list(conns.keys())
            for cat, conns in self._connectors.items()
        }

    def has(self, category: str, name: str) -> bool:
        cat = self._connectors.get(category)
        if not cat:
            return False
        return name in cat


registry = Registry()
