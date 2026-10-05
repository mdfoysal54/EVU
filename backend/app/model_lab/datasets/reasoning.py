from __future__ import annotations

from app.model_lab.experience.schema import (
    ExperienceRecord,
)

from .schema import ReasoningExample


REASONING_TYPES = {
    "reasoning",
    "math",
    "logic",
    "analysis",
    "planning",
    "research",
}


def build_reasoning_dataset(
    experiences: list[ExperienceRecord],
    minimum_score: float = 0.75,
) -> list[ReasoningExample]:

    output = []

    for experience in experiences:

        if experience.task_type not in REASONING_TYPES:
            continue

        if not experience.evaluation:
            continue

        score = (
            experience.evaluation.overall
        )

        if score < minimum_score:
            continue

        output.append(
            ReasoningExample(
                example_id=experience.experience_id,
                prompt=experience.prompt,
                answer=experience.response,
                reasoning_type=experience.task_type,
                quality_score=score,
                metadata={
                    "source": "evu_experience",
                    "model": experience.model,
                    "provider": experience.provider,
                },
            )
        )

    return output