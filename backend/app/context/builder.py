from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class ContextItem:
    content: Any
    source: str = "unknown"
    priority: float = 0.5
    token_estimate: int = 0
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class BuiltContext:
    items: List[ContextItem] = field(
        default_factory=list
    )

    system: str = ""
    instructions: str = ""
    user_input: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def total_token_estimate(self) -> int:
        return sum(
            item.token_estimate
            for item in self.items
        )

    def as_text(self) -> str:
        sections: list[str] = []

        if self.system:
            sections.append(
                f"[SYSTEM]\n{self.system}"
            )

        if self.instructions:
            sections.append(
                f"[INSTRUCTIONS]\n{self.instructions}"
            )

        for item in self.items:
            sections.append(
                f"[{item.source.upper()}]\n{item.content}"
            )

        if self.user_input:
            sections.append(
                f"[USER]\n{self.user_input}"
            )

        return "\n\n".join(sections)


class ContextBuilder:
    """
    Builds an ordered context from multiple EVU sources.

    Typical future sources:
      - conversation memory
      - RAG
      - tools
      - web research
      - agent collaboration
      - user profile
      - system instructions
    """

    def __init__(
        self,
        max_tokens: int = 16_000,
    ) -> None:
        self.max_tokens = max_tokens

    @staticmethod
    def estimate_tokens(
        text: Any,
    ) -> int:
        value = str(text)

        # Lightweight estimate. A real tokenizer can replace this.
        return max(
            1,
            len(value) // 4,
        )

    def add(
        self,
        context: BuiltContext,
        content: Any,
        source: str = "unknown",
        priority: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ContextItem:
        item = ContextItem(
            content=content,
            source=source,
            priority=priority,
            token_estimate=self.estimate_tokens(content),
            metadata=dict(metadata or {}),
        )

        context.items.append(item)

        return item

    def build(
        self,
        *,
        system: str = "",
        instructions: str = "",
        user_input: str = "",
        items: Optional[Iterable[ContextItem]] = None,
    ) -> BuiltContext:
        context = BuiltContext(
            system=system,
            instructions=instructions,
            user_input=user_input,
            items=list(items or []),
        )

        context.items.sort(
            key=lambda item: item.priority,
            reverse=True,
        )

        return self.fit(context)

    def fit(
        self,
        context: BuiltContext,
    ) -> BuiltContext:
        remaining = self.max_tokens

        fitted: list[ContextItem] = []

        for item in context.items:
            if item.token_estimate <= remaining:
                fitted.append(item)
                remaining -= item.token_estimate

        context.items = fitted

        context.metadata[
            "estimated_tokens"
        ] = context.total_token_estimate

        context.metadata[
            "max_tokens"
        ] = self.max_tokens

        return context