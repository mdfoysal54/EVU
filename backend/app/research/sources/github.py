from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..provenance import EvidenceType, ResearchSource


@dataclass
class GitHubSourceConfig:
    token: str | None = None
    timeout: float = 20.0


class GitHubSource:
    """GitHub research adapter using an injected HTTP transport."""

    API_ROOT = "https://api.github.com"

    def __init__(self, config: GitHubSourceConfig | None = None, transport=None) -> None:
        self.config = config or GitHubSourceConfig()
        self.transport = transport

    def _request(self, path: str, **params: Any) -> Any:
        if self.transport is None:
            raise RuntimeError("No GitHub transport configured")
        headers = {"Accept": "application/vnd.github+json"}
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        return self.transport(
            self.API_ROOT + path,
            params=params,
            headers=headers,
            timeout=self.config.timeout,
        )

    def repository(self, owner: str, repo: str) -> ResearchSource:
        data = self._request(f"/repos/{owner}/{repo}")
        content = str(data.get("description") or "")
        return ResearchSource(
            url=data.get("html_url", f"https://github.com/{owner}/{repo}"),
            title=data.get("full_name", f"{owner}/{repo}"),
            source_type="github",
            publisher="GitHub",
            author=str(data.get("owner", {}).get("login", owner)),
            content=content,
            snippet=content[:500],
            evidence_type=EvidenceType.PRIMARY,
            metadata=data,
        )

    def search_repositories(self, query: str, limit: int = 10) -> list[ResearchSource]:
        data = self._request("/search/repositories", q=query, per_page=min(limit, 100))
        return [
            ResearchSource(
                url=item.get("html_url", ""),
                title=item.get("full_name", ""),
                source_type="github",
                publisher="GitHub",
                author=str(item.get("owner", {}).get("login", "")),
                content=item.get("description") or "",
                snippet=(item.get("description") or "")[:500],
                evidence_type=EvidenceType.PRIMARY,
                metadata=item,
            )
            for item in data.get("items", [])
        ]
