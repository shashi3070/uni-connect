from __future__ import annotations

from typing import Any, Optional, Type, Union

from uniconnect.core.base import BaseConnector
from uniconnect.core.config import Config, detect_type, load_env_config, merge_configs
from uniconnect.core.exceptions import ConfigurationError
from uniconnect.core.registry import registry


def _identify_connector(config: dict) -> tuple[str, str]:
    detected = detect_type(config)
    if detected:
        return detected

    type_name = config.get("type", "")
    if not type_name:
        uri = config.get("uri", "")
        if not uri:
            raise ConfigurationError(
                "Cannot determine connector type. Provide 'type', 'uri', or use a URI string."
            )
        raise ConfigurationError(f"Cannot detect connector type from URI: {uri}")

    for category, conns in registry._connectors.items():
        if type_name in conns:
            return category, type_name
        for alias, _cls in conns.items():
            if type_name == alias:
                return category, alias

    raise ConfigurationError(
        f"Unknown connector type '{type_name}'. "
        f"Available: {registry.list_connectors()}"
    )


class ConnectionFactory:
    @staticmethod
    def create(
        connector_type: Union[str, dict],
        config: Optional[dict] = None,
        **kwargs: Any,
    ) -> BaseConnector:
        if isinstance(connector_type, str):
            if "://" in connector_type:
                cfg = {"uri": connector_type}
            else:
                cfg = {"type": connector_type}
        elif isinstance(connector_type, dict):
            cfg = dict(connector_type)
        else:
            raise ConfigurationError(
                "connector_type must be a string (type name or URI) or a dict"
            )

        if config:
            cfg = merge_configs(cfg, config)
        if kwargs:
            cfg = merge_configs(cfg, kwargs)

        env_cfg = load_env_config()
        cfg = merge_configs(env_cfg, cfg)

        category, name = _identify_connector(cfg)
        driver = cfg.get("driver")
        cls = registry.get(category, name, driver=driver)
        return cls(config=cfg)

    @staticmethod
    def get_connector(
        connector_type: str,
        config: Optional[dict] = None,
        **kwargs: Any,
    ) -> BaseConnector:
        return ConnectionFactory.create(connector_type, config, **kwargs)


connect = ConnectionFactory.create
get_connector = ConnectionFactory.get_connector
