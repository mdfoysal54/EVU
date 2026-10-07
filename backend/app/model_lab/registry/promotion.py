from __future__ import annotations

from dataclasses import dataclass

from .gates import (
    GateResult,
    PromotionGate,
    evaluate_gate,
)


@dataclass
class PromotionDecision:
    approved: bool
    source_status: str
    target_status: str
    gate: GateResult

    def to_dict(self) -> dict:
        return {
            "approved": self.approved,
            "source_status": (
                self.source_status
            ),
            "target_status": (
                self.target_status
            ),
            "gate": {
                "passed": self.gate.passed,
                "reasons": self.gate.reasons,
                "metrics": self.gate.metrics,
            },
        }


def decide_promotion(
    source_status: str,
    target_status: str,
    *,
    benchmark_score: float,
    pass_rate: float,
    safety_score: float,
    regression: float,
    gate: PromotionGate | None = None,
) -> PromotionDecision:
    gate_result = evaluate_gate(
        benchmark_score=benchmark_score,
        pass_rate=pass_rate,
        safety_score=safety_score,
        regression=regression,
        gate=gate,
    )

    return PromotionDecision(
        approved=gate_result.passed,
        source_status=source_status,
        target_status=target_status,
        gate=gate_result,
    )