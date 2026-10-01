from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..provenance import EvidenceType, ResearchSource


@dataclass
class APISourceConfig:
    base_url: str
    name: str = "api"
    headers: dict[str, str] | None = None
    timeout: float = 20.0


class APISource:
    """Adapter for application-specific JSON APIs.

    Network transport is injected to keep EVU's research layer independent
    from requests/httpx and to allow the existing web client to be reused.
    """

    def __init__(self, config: APISourceConfig, transport=None) -> None:
        self.config = config
        self.transport = transport

    def fetch(self, path: str = "", **params: Any) -> ResearchSource:
        if self.transport is None:
            raise RuntimeError("No API transport configured")

        result = self.transport(
            self.config.base_url.rstrip("/") + "/" + path.lstrip("/"),
            params=params,
            headers=self.config.headers or {},
            timeout=self.config.timeout,
        )

        if not isinstance(result, dict):
            result = {"data": result}

        content = str(result.get("content") or result.get("data") or result)
        return ResearchSource(
            url=self.config.base_url,
            title=str(result.get("title", self.config.name)),
            source_type="api",
            publisher=self.config.name,
            content=content,
            snippet=content[:500],
            evidence_type=EvidenceType.PRIMARY,
            metadata=result,
        )
