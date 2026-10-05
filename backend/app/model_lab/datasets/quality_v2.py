from __future__ import annotations

from dataclasses import dataclass

from app.model_lab.evaluation.quality import (
    QualityConfig,
    score_instruction,
)

from .language import detect_language
from .safety import (
    is_safe_training_example,
)


@dataclass
class CuratedRecord:
    record: dict
    score: float
    language: str
    accepted: bool
    reasons: list[str]


def evaluate_record(
    record: dict,
    config: QualityConfig | None = None,
) -> CuratedRecord:
    config = config or QualityConfig()

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

    combined = (
        instruction
        + "\n"
        + response
    )

    quality = score_instruction(
        instruction,
        response,
    )

    reasons = list(
        quality.reasons
    )

    if not is_safe_training_example(
        combined
    ):
        reasons.append(
            "safety_filter"
        )

    language = detect_language(
        combined
    )

    accepted = (
        quality.accepted
        and "safety_filter"
        not in reasons
    )

    return CuratedRecord(
        record=record,
        score=quality.score,
        language=language,
        accepted=accepted,
        reasons=reasons,
    )