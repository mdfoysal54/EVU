from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from .models import MemoryEdge, MemoryNode


@dataclass(frozen=True)
class ExtractionResult:
    nodes: tuple[MemoryNode, ...]
    edges: tuple[MemoryEdge, ...]


class MemoryGraphExtractor:
    """Rule-based baseline with optional LLM/model extraction."""

    _ENTITY_RE = re.compile(
        r"\b[A-Z][\w-]{2,}"
        r"(?:\s+[A-Z][\w-]{2,})*\b"
    )

    def __init__(
        self,
        model_extractor: Callable[
            [str],
            dict
        ] | None = None,
    ) -> None:
        self.model_extractor = model_extractor

    def extract(
        self,
        text: str,
        source_memory_id: str | None = None,
    ) -> ExtractionResult:
        if self.model_extractor is not None:
            try:
                raw = (
                    self.model_extractor(text)
                    or {}
                )

                return self._from_model(
                    raw,
                    source_memory_id,
                )
            except Exception:
                pass

        return self._rule_extract(
            text,
            source_memory_id,
        )

    def _from_model(
        self,
        raw: dict,
        source_memory_id: str | None,
    ) -> ExtractionResult:
        nodes: list[MemoryNode] = []

        for item in raw.get("nodes", []):
            if isinstance(item, MemoryNode):
                nodes.append(item)
                continue

            nodes.append(
                MemoryNode(
                    id=str(
                        item.get("id")
                        or ""
                    ),
                    kind=str(
                        item.get(
                            "kind",
                            "entity",
                        )
                    ),
                    label=str(
                        item.get(
                            "label",
                            "",
                        )
                    ),
                    content=str(
                        item.get(
                            "content",
                            "",
                        )
                    ),
                    properties=dict(
                        item.get(
                            "properties",
                            {},
                        )
                    ),
                    source_memory_id=(
                        source_memory_id
                        or item.get(
                            "source_memory_id"
                        )
                    ),
                    confidence=float(
                        item.get(
                            "confidence",
                            1.0,
                        )
                    ),
                )
            )

        edges: list[MemoryEdge] = []

        for item in raw.get("edges", []):
            if isinstance(item, MemoryEdge):
                edges.append(item)
                continue

            edges.append(
                MemoryEdge(
                    source=str(
                        item["source"]
                    ),
                    target=str(
                        item["target"]
                    ),
                    relation=str(
                        item.get(
                            "relation",
                            "related_to",
                        )
                    ),
                    weight=float(
                        item.get(
                            "weight",
                            1.0,
                        )
                    ),
                    properties=dict(
                        item.get(
                            "properties",
                            {},
                        )
                    ),
                )
            )

        return ExtractionResult(
            tuple(nodes),
            tuple(edges),
        )

    def _rule_extract(
        self,
        text: str,
        source_memory_id: str | None,
    ) -> ExtractionResult:
        labels = list(
            dict.fromkeys(
                self._ENTITY_RE.findall(
                    text or ""
                )
            )
        )

        nodes = [
            MemoryNode(
                kind="entity",
                label=label,
                content=label,
                source_memory_id=source_memory_id,
            )
            for label in labels[:50]
        ]

        edges: list[MemoryEdge] = []

        for left, right in zip(
            nodes,
            nodes[1:],
        ):
            edges.append(
                MemoryEdge(
                    source=left.id,
                    target=right.id,
                    relation="co_occurs_with",
                    weight=0.5,
                )
            )

        return ExtractionResult(
            tuple(nodes),
            tuple(edges),
        )