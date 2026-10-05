from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .quality import QualityConfig, score_instruction


@dataclass
class DatasetEvaluation:
    total: int
    accepted: int
    rejected: int
    average_score: float
    rejection_reasons: dict[str, int] = field(
        default_factory=dict
    )

    @property
    def acceptance_rate(self) -> float:
        if self.total == 0:
            return 0.0

        return self.accepted / self.total


def evaluate_records(
    records: Iterable[dict],
    config: QualityConfig | None = None,
) -> DatasetEvaluation:
    config = config or QualityConfig()

    total = 0
    accepted = 0
    rejected = 0
    scores: list[float] = []
    reasons: dict[str, int] = {}

    for record in records:
        total += 1

        instruction = str(
            record.get("instruction")
            or record.get("prompt")
            or record.get("input")
            or ""
        )

        response = str(
            record.get("response")
            or record.get("output")
            or record.get("answer")
            or ""
        )

        result = score_instruction(
            instruction,
            response,
        )

        scores.append(result.score)

        if result.accepted:
            accepted += 1
        else:
            rejected += 1

        for reason in result.reasons:
            reasons[reason] = (
                reasons.get(reason, 0) + 1
            )

    average = (
        sum(scores) / len(scores)
        if scores
        else 0.0
    )

    return DatasetEvaluation(
        total=total,
        accepted=accepted,
        rejected=rejected,
        average_score=average,
        rejection_reasons=reasons,
    )