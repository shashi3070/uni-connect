from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    import requests
except ImportError:
    requests = None


class OAuth2Connector(SyncConnector):
    name = "oauth2"
    description = "OAuth 2.0 authentication"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._token: dict[str, Any] = {}

    def connect(self) -> None:
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")
        self._connected = True

    def close(self) -> None:
        self._token = {}
        self._connected = False

    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        client_id = self.config.get("client_id", "")
        authorization_url = self.config.get("authorization_url", "")
        scopes = self.config.get("scopes", [])

        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
        }
        if state:
            params["state"] = state

        import urllib.parse
        return f"{authorization_url}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str, redirect_uri: str) -> dict[str, Any]:
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")
        token_url = self.config.get("token_url", "")
        client_id = self.config.get("client_id", "")
        client_secret = self.config.get("client_secret", "")

        resp = requests.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        self._token = resp.json()
        return self._token

    def refresh_token(self) -> dict[str, Any]:
        if requests is None:
            raise ImportError("requests is required. Install with: pip install requests")
        token_url = self.config.get("token_url", "")
        client_id = self.config.get("client_id", "")
        client_secret = self.config.get("client_secret", "")
        refresh_token = self._token.get("refresh_token", "")

        resp = requests.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        self._token.update(resp.json())
        return self._token

    def get_token(self) -> dict[str, Any]:
        return self._token


registry.register("auth", "oauth2", OAuth2Connector)
