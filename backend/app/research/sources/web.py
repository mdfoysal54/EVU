from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from ..provenance import EvidenceType, ResearchSource


@dataclass
class WebSourceConfig:
    timeout: float = 20.0
    user_agent: str = "EVU-Research/1.0"


class WebSource:
    """Generic web source adapter using EVU's existing fetcher/transport."""

    def __init__(self, config: WebSourceConfig | None = None, transport=None) -> None:
        self.config = config or WebSourceConfig()
        self.transport = transport

    def fetch(self, url: str) -> ResearchSource:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only HTTP(S) URLs are supported")
        if self.transport is None:
            raise RuntimeError("No web transport configured")

        result = self.transport(
            url,
            headers={"User-Agent": self.config.user_agent},
            timeout=self.config.timeout,
        )

        if isinstance(result, dict):
            title = str(result.get("title", ""))
            content = str(result.get("text") or result.get("content") or "")
            metadata: dict[str, Any] = dict(result)
        else:
            title = ""
            content = str(result)
            metadata = {}

        return ResearchSource(
            url=url,
            title=title or parsed.netloc,
            source_type="web",
            publisher=parsed.netloc,
            content=content,
            snippet=content[:500],
            evidence_type=EvidenceType.SECONDARY,
            metadata=metadata,
        )
