from __future__ import annotations

from dataclasses import dataclass
from .quality import text_quality_score


@dataclass
class FilterConfig:
    min_chars: int = 20
    max_chars: int = 2_000_000
    min_quality: float = 0.25


class QualityFilter:
    def __init__(self, config: FilterConfig | None = None) -> None:
        self.config = config or FilterConfig()

    def accept(self, text: str) -> bool:
        size = len(text.strip())
        if size < self.config.min_chars or size > self.config.max_chars:
            return False
        return text_quality_score(text) >= self.config.min_quality