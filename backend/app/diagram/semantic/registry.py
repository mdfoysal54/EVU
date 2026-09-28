from __future__ import annotations

from .patterns import PATTERNS, SemanticPattern


class SemanticPatternRegistry:
    def __init__(self) -> None:
        self._patterns: dict[str, SemanticPattern] = {
            pattern.name: pattern
            for pattern in PATTERNS
        }

    def all(self) -> list[SemanticPattern]:
        return list(self._patterns.values())

    def get(self, name: str) -> SemanticPattern | None:
        return self._patterns.get(name)

    def find_by_type(self, diagram_type: str) -> list[SemanticPattern]:
        return [
            pattern
            for pattern in self._patterns.values()
            if pattern.diagram_type == diagram_type
        ]