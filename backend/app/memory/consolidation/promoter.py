from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class PromotionDecision:
    promote: bool
    score: float
    reasons: tuple[str, ...]


class MemoryPromoter:
    """Scores candidate memories for durable promotion."""

    def __init__(
        self,
        threshold: float = 0.65,
    ) -> None:
        self.threshold = threshold

    def score(
        self,
        metadata: Mapping[
            str,
            Any
        ] | None = None,
    ) -> PromotionDecision:
        data = dict(metadata or {})

        score = 0.0
        reasons: list[str] = []

        if data.get(
            "explicitly_saved"
        ):
            score += 0.55
            reasons.append(
                "explicitly_saved"
            )

        if data.get(
            "repeated_count",
            0,
        ) >= 2:
            score += 0.20
            reasons.append("repeated")

        if data.get(
            "successful_use_count",
            0,
        ) >= 2:
            score += 0.15
            reasons.append(
                "successfully_reused"
            )

        if data.get("importance") is not None:
            score += (
                0.10
                * max(
                    0.0,
                    min(
                        1.0,
                        float(
                            data["importance"]
                        ),
                    ),
                )
            )
            reasons.append(
                "importance_signal"
            )

        if data.get(
            "user_confirmed"
        ):
            score += 0.20
            reasons.append(
                "user_confirmed"
            )

        score = min(
            1.0,
            score,
        )

        return PromotionDecision(
            score >= self.threshold,
            score,
            tuple(reasons),
        )