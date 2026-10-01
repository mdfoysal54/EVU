from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Citation:
    """A precise reference to evidence used by an EVU research answer."""

    source_id: str
    title: str = ""
    url: str = ""
    quote: str = ""
    locator: str = ""
    publisher: str = ""
    published_at: datetime | None = None
    accessed_at: datetime = field(default_factory=utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "quote": self.quote,
            "locator": self.locator,
            "publisher": self.publisher,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "accessed_at": self.accessed_at.isoformat(),
            "metadata": dict(self.metadata),
        }


@dataclass
class CitationSet:
    citations: list[Citation] = field(default_factory=list)

    def add(self, citation: Citation) -> Citation:
        self.citations.append(citation)
        return citation

    def extend(self, citations: list[Citation]) -> None:
        self.citations.extend(citations)

    def for_source(self, source_id: str) -> list[Citation]:
        return [c for c in self.citations if c.source_id == source_id]

    def to_dict(self) -> dict[str, Any]:
        return {"citations": [c.to_dict() for c in self.citations]}
