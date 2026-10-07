from __future__ import annotations

from dataclasses import dataclass

from .evaluator import (
    ImprovementEvaluation,
)


@dataclass
class ImprovementPromotion:
    approved: bool
    reason: str


def should_promote(
    evaluation: ImprovementEvaluation,
    *,
    allow_auto_promotion: bool,
) -> ImprovementPromotion:
    if not evaluation.accepted:
        return ImprovementPromotion(
            approved=False,
            reason=(
                "candidate_failed_evaluation"
            ),
        )

    if not allow_auto_promotion:
        return ImprovementPromotion(
            approved=False,
            reason=(
                "manual_approval_required"
            ),
        )

    return ImprovementPromotion(
        approved=True,
        reason="candidate_passed_all_gates",
    )