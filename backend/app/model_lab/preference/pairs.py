from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PreferencePair:
    prompt: str
    chosen: str
    rejected: str
    chosen_score: float
    rejected_score: float
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "prompt": self.prompt,
            "chosen": self.chosen,
            "rejected": self.rejected,
            "chosen_score": self.chosen_score,
            "rejected_score": self.rejected_score,
            "metadata": self.metadata,
        }


def make_pair(
    prompt: str,
    candidate_a: str,
    candidate_b: str,
    score_a: float,
    score_b: float,
    *,
    min_margin: float = 0.05,
) -> PreferencePair | None:
    if abs(score_a - score_b) < min_margin:
        return None

    if score_a > score_b:
        chosen = candidate_a
        rejected = candidate_b
        chosen_score = score_a
        rejected_score = score_b
    else:
        chosen = candidate_b
        rejected = candidate_a
        chosen_score = score_b
        rejected_score = score_a

    return PreferencePair(
        prompt=prompt,
        chosen=chosen,
        rejected=rejected,
        chosen_score=chosen_score,
        rejected_score=rejected_score,
        metadata={
            "source": "automated_evaluator",
            "margin": abs(
                score_a - score_b
            ),
        },
    )