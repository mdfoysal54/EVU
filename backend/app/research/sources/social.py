from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..provenance import EvidenceType, ResearchSource


@dataclass
class SocialSourceConfig:
    platform: str
    timeout: float = 20.0


class SocialSource:
    """Generic social-platform adapter. Use official APIs/transports only."""

    def __init__(self, config: SocialSourceConfig, transport=None) -> None:
        self.config = config
        self.transport = transport

    def search(self, query: str, limit: int = 10) -> list[ResearchSource]:
        if self.transport is None:
            raise RuntimeError("No social transport configured")

        payload = self.transport(
            query=query,
            limit=limit,
            timeout=self.config.timeout,
        )

        if isinstance(payload, dict):
            items = payload.get("items", [])
        else:
            items = payload

        results = []
        for item in items or []:
            if not isinstance(item, dict):
                item = {"content": str(item)}
            content = str(item.get("content") or item.get("text") or "")
            results.append(
                ResearchSource(
                    url=str(item.get("url", "")),
                    title=str(item.get("title") or content[:100]),
                    source_type=f"social:{self.config.platform}",
                    publisher=self.config.platform,
                    author=str(item.get("author", "")),
                    content=content,
                    snippet=content[:500],
                    evidence_type=EvidenceType.SECONDARY,
                    metadata=item,
                )
            )
        return results
