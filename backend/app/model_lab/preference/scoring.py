from __future__ import annotations

from dataclasses import dataclass

from app.model_lab.evaluation.scorers import (
    score_response,
)


@dataclass
class CandidateScore:
    response: str
    score: float
    details: dict


def score_candidate(
    prompt: str,
    response: str,
) -> CandidateScore:
    result = score_response(
        prompt,
        response,
    )

    return CandidateScore(
        response=response,
        score=result.overall,
        details=result.to_dict(),
    )