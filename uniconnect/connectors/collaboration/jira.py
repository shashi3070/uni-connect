from __future__ import annotations

from typing import Any, Optional

from uniconnect.core.base import SyncConnector
from uniconnect.core.registry import registry
from uniconnect.core.exceptions import ConnectionError

try:
    from jira import JIRA
except ImportError:
    JIRA = None


class JiraConnector(SyncConnector):
    name = "jira"
    description = "Atlassian Jira"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._client = None

    def connect(self) -> None:
        if JIRA is None:
            raise ImportError("jira is required. Install with: pip install jira")
        url = self.config.get("url", "")
        username = self.config.get("username", "")
        api_token = self.config.get("api_token", "")
        self._client = JIRA(server=url, basic_auth=(username, api_token))
        self._connected = True

    def close(self) -> None:
        self._client = None
        self._connected = False

    def create_issue(self, project: str, summary: str, description: str = "", issuetype: str = "Task") -> dict[str, Any]:
        self._ensure_connected()
        issue_dict = {
            "project": {"key": project},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issuetype},
        }
        issue = self._client.create_issue(fields=issue_dict)
        return {"key": issue.key, "id": issue.id, "summary": summary}

    def search_issues(self, jql: str) -> list[dict[str, Any]]:
        self._ensure_connected()
        issues = self._client.search_issues(jql)
        return [{"key": i.key, "summary": i.fields.summary, "status": str(i.fields.status)} for i in issues]

    def get_issue(self, key: str) -> dict[str, Any]:
        self._ensure_connected()
        issue = self._client.issue(key)
        return {
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description,
            "status": str(issue.fields.status),
        }

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise ConnectionError("Connector is not connected. Call connect() first.")


registry.register("collaboration", "jira", JiraConnector)
