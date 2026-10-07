from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class QualityFilter:
    min_chars: int = 50
    max_chars: int = 2_000_000
    min_words: int = 8
    max_digit_ratio: float = 0.40
    max_symbol_ratio: float = 0.35
    reject_repeated_lines: bool = True

    def score(self, text: str) -> float:
        text = text.strip()

        if not text:
            return 0.0

        chars = len(text)
        words = text.split()

        if chars < self.min_chars:
            return 0.0

        if len(words) < self.min_words:
            return 0.0

        digit_ratio = sum(c.isdigit() for c in text) / max(chars, 1)

        symbols = sum(
            not c.isalnum() and not c.isspace()
            for c in text
        )

        symbol_ratio = symbols / max(chars, 1)

        score = 1.0

        if digit_ratio > self.max_digit_ratio:
            score -= 0.30

        if symbol_ratio > self.max_symbol_ratio:
            score -= 0.30

        if self.reject_repeated_lines:
            lines = [x.strip() for x in text.splitlines() if x.strip()]

            if lines:
                unique_ratio = len(set(lines)) / len(lines)

                if unique_ratio < 0.5:
                    score -= 0.40

        return max(0.0, min(1.0, score))

    def accept(self, text: str) -> bool:
        text = text.strip()

        if not text:
            return False

        if len(text) < self.min_chars:
            return False

        if len(text) > self.max_chars:
            return False

        if len(text.split()) < self.min_words:
            return False

        score = self.score(text)

        return score > 0.0