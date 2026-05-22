from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    from github import Github
except ImportError:
    Github = None


class GitHubConnector(SyncConnector):
    name = "github"
    description = "GitHub"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None
        self._repo = None

    def connect(self) -> None:
        if Github is None:
            raise ImportError("PyGithub is required. Install with: pip install PyGithub")
        token = self.config.get("token", "")
        self._client = Github(token)
        owner = self.config.get("owner", "")
        repo = self.config.get("repo", "")
        if owner and repo:
            self._repo = self._client.get_repo(f"{owner}/{repo}")
        self._connected = True

    def close(self) -> None:
        self._repo = None
        self._client = None
        self._connected = False

    def list_repos(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        repos = self._client.get_user().get_repos()
        return [{"name": r.name, "full_name": r.full_name, "url": r.html_url} for r in repos]

    def get_file(self, path: str, ref: str = "main") -> str:
        self._ensure_connected()
        if self._repo is None:
            raise RuntimeError("No repository configured. Provide owner and repo in config.")
        content = self._repo.get_contents(path, ref=ref)
        return content.decoded_content.decode("utf-8")

    def create_issue(self, title: str, body: str = "") -> dict[str, Any]:
        self._ensure_connected()
        if self._repo is None:
            raise RuntimeError("No repository configured. Provide owner and repo in config.")
        issue = self._repo.create_issue(title=title, body=body)
        return {"number": issue.number, "title": issue.title, "url": issue.html_url}

    def list_issues(self, state: str = "open") -> list[dict[str, Any]]:
        self._ensure_connected()
        if self._repo is None:
            raise RuntimeError("No repository configured. Provide owner and repo in config.")
        issues = self._repo.get_issues(state=state)
        return [{"number": i.number, "title": i.title, "state": i.state, "url": i.html_url} for i in issues]

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("collaboration", "github", GitHubConnector)
