from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any
from uuid import uuid4

from .deduplicator import (
    DuplicateGroup,
    MemoryDeduplicator,
)
from .promoter import (
    MemoryPromoter,
    PromotionDecision,
)
from .scheduler import (
    ConsolidationScheduler,
)
from .summarizer import (
    MemorySummarizer,
    SummaryResult,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class MemoryItem:
    id: str = field(
        default_factory=lambda: str(uuid4())
    )
    content: str = ""
    metadata: dict[str, Any] = field(
        default_factory=dict
    )
    durable: bool = False
    created_at: datetime = field(
        default_factory=utcnow
    )
    updated_at: datetime = field(
        default_factory=utcnow
    )

    def touch(self) -> None:
        self.updated_at = utcnow()


@dataclass(frozen=True)
class ConsolidationReport:
    processed: int
    duplicate_groups: tuple[
        DuplicateGroup,
        ...
    ]
    promoted: tuple[str, ...]
    summary: SummaryResult | None


class MemoryConsolidationService:
    """Coordinates EVU memory consolidation."""

    def __init__(
        self,
        deduplicator: MemoryDeduplicator | None = None,
        summarizer: MemorySummarizer | None = None,
        promoter: MemoryPromoter | None = None,
        scheduler: ConsolidationScheduler | None = None,
    ) -> None:
        self.deduplicator = (
            deduplicator
            or MemoryDeduplicator()
        )

        self.summarizer = (
            summarizer
            or MemorySummarizer()
        )

        self.promoter = (
            promoter
            or MemoryPromoter()
        )

        self.scheduler = (
            scheduler
            or ConsolidationScheduler()
        )

        self._items: dict[
            str,
            MemoryItem
        ] = {}

        self._lock = RLock()

    def add(
        self,
        item: MemoryItem,
    ) -> MemoryItem:
        with self._lock:
            self._items[item.id] = item

        return item

    def get(
        self,
        item_id: str,
    ) -> MemoryItem | None:
        return self._items.get(item_id)

    def items(
        self,
        *,
        durable: bool | None = None,
    ) -> list[MemoryItem]:
        values = list(
            self._items.values()
        )

        if durable is not None:
            values = [
                item
                for item in values
                if item.durable == durable
            ]

        return values

    def promote(
        self,
        item_id: str,
    ) -> PromotionDecision:
        item = self._items[item_id]

        decision = self.promoter.score(
            item.metadata
        )

        if decision.promote:
            item.durable = True
            item.touch()

        return decision

    def consolidate(
        self,
        *,
        include_summary: bool = True,
        summary_limit: int = 20,
    ) -> ConsolidationReport:
        items = self.items(
            durable=False
        )

        groups = (
            self.deduplicator.find_groups(
                (
                    item.id,
                    item.content,
                )
                for item in items
            )
        )

        promoted: list[str] = []

        for item in items:
            decision = self.promoter.score(
                item.metadata
            )

            if decision.promote:
                item.durable = True
                item.touch()

                promoted.append(
                    item.id
                )

        summary = None

        if include_summary and items:
            summary = self.summarizer.summarize(
                [
                    item.content
                    for item in items[
                        :summary_limit
                    ]
                ]
            )

        return ConsolidationReport(
            processed=len(items),
            duplicate_groups=tuple(
                groups
            ),
            promoted=tuple(
                promoted
            ),
            summary=summary,
        )

    def schedule(
        self,
        *,
        delay_seconds: float = 0,
        interval_seconds: float | None = None,
    ) -> str:
        return self.scheduler.schedule(
            self.consolidate,
            delay_seconds=delay_seconds,
            interval_seconds=interval_seconds,
        )

    def run_scheduled(
        self,
    ) -> list[tuple[str, object]]:
        return self.scheduler.run_due()