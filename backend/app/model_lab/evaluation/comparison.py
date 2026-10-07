from __future__ import annotations

from dataclasses import dataclass

from .model_eval import ModelEvaluation


@dataclass
class ModelComparison:
    winner: str
    score_delta: float
    candidate: ModelEvaluation
    baseline: ModelEvaluation

    def to_dict(self) -> dict:
        return {
            "winner": self.winner,
            "score_delta": self.score_delta,
            "candidate": (
                self.candidate.to_dict()
            ),
            "baseline": (
                self.baseline.to_dict()
            ),
        }


def compare_models(
    baseline: ModelEvaluation,
    candidate: ModelEvaluation,
) -> ModelComparison:
    baseline_score = (
        baseline.deployment_score()
    )

    candidate_score = (
        candidate.deployment_score()
    )

    delta = (
        candidate_score
        - baseline_score
    )

    if delta > 0:
        winner = "candidate"
    elif delta < 0:
        winner = "baseline"
    else:
        winner = "tie"

    return ModelComparison(
        winner=winner,
        score_delta=delta,
        candidate=candidate,
        baseline=baseline,
    )