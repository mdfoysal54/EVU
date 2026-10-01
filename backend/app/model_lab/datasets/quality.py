from __future__ import annotations

import math
import re


def text_quality_score(text: str) -> float:
    text = text.strip()
    if not text:
        return 0.0
    length = len(text)
    alpha = sum(ch.isalpha() for ch in text)
    printable = sum(ch.isprintable() or ch in "\n\t" for ch in text)
    words = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
    if not words:
        return 0.0
    alpha_ratio = alpha / length
    printable_ratio = printable / length
    repetition = 1.0 - (len(set(words)) / max(1, len(words)))
    length_score = min(1.0, math.log1p(length) / math.log1p(4000))
    return max(
        0.0,
        min(
            1.0,
            0.30 * alpha_ratio
            + 0.25 * printable_ratio
            + 0.30 * (1.0 - repetition)
            + 0.15 * length_score,
        ),
    )