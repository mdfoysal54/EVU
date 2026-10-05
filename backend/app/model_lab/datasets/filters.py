from __future__ import annotations

from typing import Iterable

from app.model_lab.experience.schema import (
    ExperienceRecord,
)


def quality_score(
    experience: ExperienceRecord,
) -> float:

    if experience.evaluation is None:
        return 0.0

    return float(
        experience.evaluation.overall
    )


def successful_experiences(
    experiences: Iterable[
        ExperienceRecord
    ],
    minimum_score: float = 0.70,
) -> list[ExperienceRecord]:

    result = []

    for experience in experiences:

        score = quality_score(
            experience
        )

        if not experience.success:
            continue

        if score < minimum_score:
            continue

        result.append(
            experience
        )

    return result


def by_task_type(
    experiences: Iterable[
        ExperienceRecord
    ],
    task_type: str,
) -> list[ExperienceRecord]:

    return [
        experience
        for experience in experiences
        if experience.task_type
        == task_type
    ]