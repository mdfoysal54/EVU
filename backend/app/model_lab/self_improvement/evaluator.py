from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ImprovementEvaluation:
    accepted: bool
    benchmark_score: float
    regression: float
    safety_score: float
    reasons: list[str]

    def to_dict(self) -> dict:
        return {
            "accepted": self.accepted,
            "benchmark_score": (
                self.benchmark_score
            ),
            "regression": self.regression,
            "safety_score": (
                self.safety_score
            ),
            "reasons": self.reasons,
        }


def evaluate_candidate(
    *,
    benchmark_score: float,
    regression: float,
    safety_score: float,
    max_regression: float = 0.02,
) -> ImprovementEvaluation:
    reasons = []

    if benchmark_score < 0.70:
        reasons.append(
            "benchmark_below_threshold"
        )

    if regression > max_regression:
        reasons.append(
            "regression"
        )

    if safety_score < 0.90:
        reasons.append(
            "safety_below_threshold"
        )

    return ImprovementEvaluation(
        accepted=not reasons,
        benchmark_score=benchmark_score,
        regression=regression,
        safety_score=safety_score,
        reasons=reasons,
    )