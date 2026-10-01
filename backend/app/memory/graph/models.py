from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class MemoryNode:
    id: str = field(
        default_factory=lambda: str(uuid4())
    )
    kind: str = "memory"
    label: str = ""
    content: str = ""
    properties: dict[str, Any] = field(
        default_factory=dict
    )
    source_memory_id: str | None = None
    confidence: float = 1.0
    created_at: datetime = field(
        default_factory=utcnow
    )
    updated_at: datetime = field(
        default_factory=utcnow
    )

    def touch(self) -> None:
        self.updated_at = utcnow()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)

        data["created_at"] = (
            self.created_at.isoformat()
        )
        data["updated_at"] = (
            self.updated_at.isoformat()
        )

        return data


@dataclass
class MemoryEdge:
    id: str = field(
        default_factory=lambda: str(uuid4())
    )
    source: str = ""
    target: str = ""
    relation: str = "related_to"
    weight: float = 1.0
    properties: dict[str, Any] = field(
        default_factory=dict
    )
    created_at: datetime = field(
        default_factory=utcnow
    )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)

        data["created_at"] = (
            self.created_at.isoformat()
        )

        return data