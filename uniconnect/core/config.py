from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Optional


_URI_PATTERN = re.compile(r"^(\w+):\/\/")


def parse_connection_string(uri: str) -> dict:
    scheme = _URI_PATTERN.match(uri)
    if scheme:
        return {"type": scheme.group(1), "uri": uri}
    return {"type": "unknown", "uri": uri}


def detect_type(config: dict) -> Optional[tuple[str, str]]:
    uri = config.get("uri", "")
    if not uri:
        return None

    scheme_map = {
        "s3": ("storage", "s3"),
        "gs": ("storage", "gcs"),
        "gcs": ("storage", "gcs"),
        "azure": ("storage", "azure_blob"),
        "ftp": ("storage", "ftp"),
        "sftp": ("storage", "sftp"),
        "file": ("storage", "local"),
        "postgresql": ("databases", "postgres"),
        "postgres": ("databases", "postgres"),
        "mysql": ("databases", "mysql"),
        "mssql": ("databases", "sqlserver"),
        "sqlserver": ("databases", "sqlserver"),
        "sqlite": ("databases", "sqlite"),
        "oracle": ("databases", "oracle"),
        "mongodb": ("databases", "mongodb"),
        "redis": ("databases", "redis"),
        "redshift": ("warehouse", "redshift"),
        "snowflake": ("warehouse", "snowflake"),
        "bigquery": ("warehouse", "bigquery"),
        "presto": ("warehouse", "presto"),
        "trino": ("warehouse", "presto"),
        "kafka": ("streaming", "kafka"),
        "rabbitmq": ("streaming", "rabbitmq"),
        "http": ("messaging", "http"),
        "https": ("messaging", "http"),
    }

    match = _URI_PATTERN.match(uri)
    if match:
        scheme = match.group(1)
        return scheme_map.get(scheme)
    return None


def load_env_config(prefix: str = "UNICONNECT_") -> dict:
    config = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):].lower()
            config[config_key] = value
    return config


def load_env_file(path: Optional[str] = None) -> dict:
    if path is None:
        path = Path.cwd() / ".env"
    else:
        path = Path(path)

    config = {}
    if not path.exists():
        return config

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        config[key] = value
    return config


def merge_configs(*configs: dict) -> dict:
    result = {}
    for c in configs:
        result.update(c)
    return result


class Config:
    def __init__(self, source: Optional[dict] = None):
        self._data = source or {}

    @classmethod
    def from_dict(cls, data: dict) -> Config:
        return cls(data)

    @classmethod
    def from_env(cls, prefix: str = "UNICONNECT_") -> Config:
        return cls(load_env_config(prefix))

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def to_dict(self) -> dict:
        return dict(self._data)

    def merge(self, other: Config) -> Config:
        merged = dict(self._data)
        merged.update(other._data)
        return Config(merged)
