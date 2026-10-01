from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..provenance import EvidenceType, ResearchSource


@dataclass
class RedditSourceConfig:
    user_agent: str = "EVU-Research/1.0"
    timeout: float = 20.0


class RedditSource:
    """Reddit adapter; transport is injected for policy/auth/network control."""

    ROOT = "https://www.reddit.com"

    def __init__(self, config: RedditSourceConfig | None = None, transport=None) -> None:
        self.config = config or RedditSourceConfig()
        self.transport = transport

    def search(self, query: str, limit: int = 10) -> list[ResearchSource]:
        if self.transport is None:
            raise RuntimeError("No Reddit transport configured")

        data = self.transport(
            f"{self.ROOT}/search.json",
            params={"q": query, "limit": min(limit, 100), "raw_json": 1},
            headers={"User-Agent": self.config.user_agent},
            timeout=self.config.timeout,
        )

        children = data.get("data", {}).get("children", [])
        results: list[ResearchSource] = []
        for child in children:
            item: dict[str, Any] = child.get("data", {})
            permalink = item.get("permalink", "")
            results.append(
                ResearchSource(
                    url=(self.ROOT + permalink) if permalink else "",
                    title=item.get("title", ""),
                    source_type="reddit",
                    publisher="Reddit",
                    author=item.get("author", ""),
                    content=item.get("selftext", ""),
                    snippet=item.get("selftext", "")[:500],
                    evidence_type=EvidenceType.SECONDARY,
                    metadata=item,
                )
            )
        return results
