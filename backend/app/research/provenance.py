from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EvidenceType(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    USER_PROVIDED = "user_provided"
    GENERATED = "generated"


class ProvenanceRelation(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVED_FROM = "derived_from"
    QUOTES = "quotes"
    SUMMARIZES = "summarizes"
    RELATED = "related"


@dataclass
class ResearchSource:
    id: str = field(default_factory=lambda: str(uuid4()))
    url: str = ""
    title: str = ""
    source_type: str = "web"
    publisher: str = ""
    author: str = ""
    published_at: datetime | None = None
    accessed_at: datetime = field(default_factory=utcnow)
    content: str = ""
    snippet: str = ""
    evidence_type: EvidenceType = EvidenceType.SECONDARY
    metadata: dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "source_type": self.source_type,
            "publisher": self.publisher,
            "author": self.author,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "accessed_at": self.accessed_at.isoformat(),
            "content": self.content,
            "snippet": self.snippet,
            "evidence_type": self.evidence_type.value,
            "metadata": dict(self.metadata),
            "content_hash": self.content_hash,
        }


@dataclass(frozen=True)
class ProvenanceLink:
    source_id: str
    target_id: str
    relation: ProvenanceRelation
    note: str = ""
    created_at: datetime = field(default_factory=utcnow)


class ProvenanceGraph:
    """In-memory provenance graph that can later be persisted by EVU."""

    def __init__(self) -> None:
        self.sources: dict[str, ResearchSource] = {}
        self.links: list[ProvenanceLink] = []

    def add_source(self, source: ResearchSource) -> ResearchSource:
        self.sources[source.id] = source
        return source

    def link(
        self,
        source_id: str,
        target_id: str,
        relation: ProvenanceRelation,
        note: str = "",
    ) -> ProvenanceLink:
        if source_id not in self.sources and source_id != target_id:
            raise KeyError(f"Unknown provenance source: {source_id}")
        link = ProvenanceLink(source_id, target_id, relation, note)
        self.links.append(link)
        return link

    def parents(self, target_id: str) -> list[ResearchSource]:
        ids = {
            link.source_id
            for link in self.links
            if link.target_id == target_id
        }
        return [self.sources[i] for i in ids if i in self.sources]

    def children(self, source_id: str) -> list[str]:
        return [
            link.target_id
            for link in self.links
            if link.source_id == source_id
        ]

    def trace(self, target_id: str, max_depth: int = 5) -> list[ResearchSource]:
        found: list[ResearchSource] = []
        seen: set[str] = set()
        queue: list[tuple[str, int]] = [(target_id, 0)]
        while queue:
            current, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            for link in self.links:
                if link.target_id != current or link.source_id in seen:
                    continue
                seen.add(link.source_id)
                source = self.sources.get(link.source_id)
                if source:
                    found.append(source)
                    queue.append((source.id, depth + 1))
        return found
