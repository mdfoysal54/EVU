from __future__ import annotations

from dataclasses import dataclass, field
import math
import re


@dataclass
class QualityResult:
    score: float
    accepted: bool
    reasons: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)


@dataclass
class QualityConfig:
    min_score: float = 0.65
    min_chars: int = 10
    max_chars: int = 200_000
    min_words: int = 3
    max_repetition_ratio: float = 0.65


_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _length_score(text: str) -> float:
    length = len(text.strip())

    if length <= 0:
        return 0.0

    if length < 10:
        return 0.1

    if length < 40:
        return 0.5

    if length < 4000:
        return 1.0

    return max(
        0.3,
        1.0 - (
            math.log1p(length / 4000)
            / math.log(100)
        ),
    )


def _repetition_score(words: list[str]) -> float:
    if not words:
        return 0.0

    normalized = [
        word.lower()
        for word in words
    ]

    unique = len(set(normalized))

    diversity = unique / len(normalized)

    return _clamp(diversity)


def score_text(
    text: str,
    config: QualityConfig | None = None,
) -> QualityResult:
    config = config or QualityConfig()

    reasons: list[str] = []

    text = text.strip()

    if not text:
        return QualityResult(
            score=0.0,
            accepted=False,
            reasons=["empty_text"],
        )

    if len(text) < config.min_chars:
        reasons.append("too_short")

    if len(text) > config.max_chars:
        reasons.append("too_long")

    words = _WORD_RE.findall(text)

    if len(words) < config.min_words:
        reasons.append("too_few_words")

    printable_ratio = (
        sum(
            1
            for char in text
            if char.isprintable() or char in "\n\t"
        )
        / max(1, len(text))
    )

    alpha_ratio = (
        sum(
            1
            for char in text
            if char.isalpha()
        )
        / max(1, len(text))
    )

    diversity = _repetition_score(words)

    repetition = 1.0 - diversity

    if repetition > config.max_repetition_ratio:
        reasons.append("high_repetition")

    length_score = _length_score(text)

    score = (
        0.30 * printable_ratio
        + 0.25 * alpha_ratio
        + 0.25 * diversity
        + 0.20 * length_score
    )

    score = _clamp(score)

    if score < config.min_score:
        reasons.append("below_quality_threshold")

    return QualityResult(
        score=score,
        accepted=(
            score >= config.min_score
            and not {
                "too_short",
                "too_long",
            }.intersection(reasons)
        ),
        reasons=reasons,
        metrics={
            "length": float(len(text)),
            "word_count": float(len(words)),
            "printable_ratio": printable_ratio,
            "alpha_ratio": alpha_ratio,
            "diversity": diversity,
            "repetition": repetition,
            "length_score": length_score,
        },
    )


def score_instruction(
    instruction: str,
    response: str,
) -> QualityResult:
    combined = (
        f"{instruction.strip()}\n"
        f"{response.strip()}"
    )

    result = score_text(combined)

    reasons = list(result.reasons)

    if not instruction.strip():
        reasons.append("missing_instruction")

    if not response.strip():
        reasons.append("missing_response")

    if instruction.strip() == response.strip():
        reasons.append("instruction_equals_response")

    score = result.score

    if "missing_instruction" in reasons:
        score *= 0.4

    if "missing_response" in reasons:
        score *= 0.2

    if "instruction_equals_response" in reasons:
        score *= 0.5

    score = _clamp(score)

    return QualityResult(
        score=score,
        accepted=score >= 0.65,
        reasons=reasons,
        metrics=result.metrics,
    )