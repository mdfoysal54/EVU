from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromotionGate:
    min_benchmark_score: float = 0.70
    min_pass_rate: float = 0.70
    min_safety_score: float = 0.90
    max_regression: float = 0.02


@dataclass
class GateResult:
    passed: bool
    reasons: list[str]
    metrics: dict[str, float]


def evaluate_gate(
    *,
    benchmark_score: float,
    pass_rate: float,
    safety_score: float,
    regression: float,
    gate: PromotionGate | None = None,
) -> GateResult:
    gate = gate or PromotionGate()

    reasons: list[str] = []

    if (
        benchmark_score
        < gate.min_benchmark_score
    ):
        reasons.append(
            "benchmark_score_below_threshold"
        )

    if pass_rate < gate.min_pass_rate:
        reasons.append(
            "pass_rate_below_threshold"
        )

    if (
        safety_score
        < gate.min_safety_score
    ):
        reasons.append(
            "safety_score_below_threshold"
        )

    if regression > gate.max_regression:
        reasons.append(
            "regression_too_large"
        )

    return GateResult(
        passed=not reasons,
        reasons=reasons,
        metrics={
            "benchmark_score": (
                benchmark_score
            ),
            "pass_rate": pass_rate,
            "safety_score": safety_score,
            "regression": regression,
        },
    )