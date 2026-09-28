from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from .builder import BuiltContext, ContextItem


@dataclass
class CompactionResult:
    context: BuiltContext
    compacted: bool
    removed_items: int
    estimated_tokens_before: int
    estimated_tokens_after: int


class ContextCompactor:
    """
    Reduces context size while preserving high-priority information.
    """

    def __init__(
        self,
        max_tokens: int,
        summarizer: Optional[
            Callable[[list[ContextItem]], str]
        ] = None,
    ) -> None:
        self.max_tokens = max_tokens
        self.summarizer = summarizer

    def compact(
        self,
        context: BuiltContext,
    ) -> CompactionResult:
        before = context.total_token_estimate

        if before <= self.max_tokens:
            return CompactionResult(
                context=context,
                compacted=False,
                removed_items=0,
                estimated_tokens_before=before,
                estimated_tokens_after=before,
            )

        items = sorted(
            context.items,
            key=lambda item: item.priority,
            reverse=True,
        )

        kept: list[ContextItem] = []
        removed: list[ContextItem] = []

        tokens = 0

        for item in items:
            if tokens + item.token_estimate <= self.max_tokens:
                kept.append(item)
                tokens += item.token_estimate
            else:
                removed.append(item)

        if removed and self.summarizer is not None:
            summary = self.summarizer(removed)

            summary_item = ContextItem(
                content=summary,
                source="compaction_summary",
                priority=0.7,
                token_estimate=max(
                    1,
                    len(summary) // 4,
                ),
            )

            # Replace lowest-priority material where possible.
            kept.append(summary_item)

            kept.sort(
                key=lambda item: item.priority,
                reverse=True,
            )

            while (
                sum(
                    item.token_estimate
                    for item in kept
                )
                > self.max_tokens
                and len(kept) > 1
            ):
                kept.pop()

        context.items = kept

        after = context.total_token_estimate

        context.metadata[
            "compacted"
        ] = True

        context.metadata[
            "removed_items"
        ] = len(removed)

        return CompactionResult(
            context=context,
            compacted=True,
            removed_items=len(removed),
            estimated_tokens_before=before,
            estimated_tokens_after=after,
        )