from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .schema import ExperienceRecord


@dataclass
class TrainingExample:
    prompt: str
    response: str
    task_type: str = "general"
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PreferenceTrainingExample:
    prompt: str
    chosen: str
    rejected: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TrajectoryTrainingExample:
    prompt: str
    response: str
    trajectory: list[dict[str, Any]]
    task_type: str = "general"
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_sft_examples(
    experiences: list[ExperienceRecord],
    minimum_score: float = 0.70,
) -> list[TrainingExample]:

    examples: list[TrainingExample] = []

    for experience in experiences:

        if not experience.evaluation:
            continue

        if not experience.evaluation.passed:
            continue

        if (
            experience.evaluation.overall
            < minimum_score
        ):
            continue

        examples.append(
            TrainingExample(
                prompt=experience.prompt,
                response=experience.response,
                task_type=experience.task_type,
                metadata={
                    "experience_id":
                        experience.experience_id,
                    "evaluation_score":
                        experience.evaluation.overall,
                    "source":
                        "evu_experience",
                },
            )
        )

    return examples


def build_preference_examples(
    experiences: list[ExperienceRecord],
    minimum_score: float = 0.70,
) -> list[PreferenceTrainingExample]:

    grouped: dict[str, list[ExperienceRecord]] = {}

    for experience in experiences:

        if not experience.evaluation:
            continue

        grouped.setdefault(
            experience.prompt,
            [],
        ).append(experience)

    examples: list[
        PreferenceTrainingExample
    ] = []

    for prompt, candidates in grouped.items():

        if len(candidates) < 2:
            continue

        ranked = sorted(
            candidates,
            key=lambda item: (
                item.evaluation.overall
                if item.evaluation
                else 0.0
            ),
            reverse=True,
        )

        chosen = ranked[0]
        rejected = ranked[-1]

        if chosen is rejected:
            continue

        chosen_score = (
            chosen.evaluation.overall
            if chosen.evaluation
            else 0.0
        )

        rejected_score = (
            rejected.evaluation.overall
            if rejected.evaluation
            else 0.0
        )

        if chosen_score < minimum_score:
            continue

        if chosen_score <= rejected_score:
            continue

        examples.append(
            PreferenceTrainingExample(
                prompt=prompt,
                chosen=chosen.response,
                rejected=rejected.response,
                metadata={
                    "chosen_experience_id":
                        chosen.experience_id,
                    "rejected_experience_id":
                        rejected.experience_id,
                    "chosen_score":
                        chosen_score,
                    "rejected_score":
                        rejected_score,
                    "source":
                        "evu_experience",
                },
            )
        )

    return examples


def build_trajectory_examples(
    experiences: list[ExperienceRecord],
    minimum_score: float = 0.70,
) -> list[TrajectoryTrainingExample]:

    examples: list[
        TrajectoryTrainingExample
    ] = []

    for experience in experiences:

        if not experience.evaluation:
            continue

        if not experience.evaluation.passed:
            continue

        if (
            experience.evaluation.overall
            < minimum_score
        ):
            continue

        trajectory = [
            step.to_dict()
            for step in experience.steps
        ]

        examples.append(
            TrajectoryTrainingExample(
                prompt=experience.prompt,
                response=experience.response,
                trajectory=trajectory,
                task_type=experience.task_type,
                metadata={
                    "experience_id":
                        experience.experience_id,
                    "evaluation_score":
                        experience.evaluation.overall,
                    "source":
                        "evu_experience",
                },
            )
        )

    return examples