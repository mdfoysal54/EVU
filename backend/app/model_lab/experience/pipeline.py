from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .dataset import (
    PreferenceTrainingExample,
    TrainingExample,
    TrajectoryTrainingExample,
    build_preference_examples,
    build_sft_examples,
    build_trajectory_examples,
)
from .evaluator import ExperienceEvaluator
from .schema import ExperienceRecord
from .store import ExperienceStore


@dataclass
class ExperiencePipelineResult:
    total_experiences: int

    accepted_experiences: int

    rejected_experiences: int

    sft_examples: list[TrainingExample]

    preference_examples: list[
        PreferenceTrainingExample
    ]

    trajectory_examples: list[
        TrajectoryTrainingExample
    ]


class ExperiencePipeline:
    """
    EVU Block 5 experience pipeline.

    Flow:

        Store
          ↓
        Evaluate
          ↓
        Filter
          ↓
        Build datasets
    """

    def __init__(
        self,
        store: ExperienceStore,
        evaluator: ExperienceEvaluator | None = None,
    ) -> None:

        self.store = store

        self.evaluator = (
            evaluator
            or ExperienceEvaluator()
        )

    def record(
        self,
        experience: ExperienceRecord,
    ) -> ExperienceRecord:

        result = self.evaluator.evaluate(
            experience
        )

        experience.evaluation = (
            result.evaluation
        )

        self.store.append(
            experience
        )

        return experience

    def evaluate_all(
        self,
        experiences: Iterable[
            ExperienceRecord
        ],
    ) -> list[ExperienceRecord]:

        evaluated: list[
            ExperienceRecord
        ] = []

        for experience in experiences:

            result = self.evaluator.evaluate(
                experience
            )

            experience.evaluation = (
                result.evaluation
            )

            evaluated.append(
                experience
            )

        return evaluated

    def build_datasets(
        self,
        experiences: list[ExperienceRecord] | None = None,
        minimum_score: float = 0.70,
    ) -> ExperiencePipelineResult:

        if experiences is None:
            experiences = self.store.load_all()

        evaluated = self.evaluate_all(
            experiences
        )

        accepted = [
            item
            for item in evaluated
            if (
                item.evaluation is not None
                and item.evaluation.passed
            )
        ]

        rejected = [
            item
            for item in evaluated
            if (
                item.evaluation is None
                or not item.evaluation.passed
            )
        ]

        sft_examples = build_sft_examples(
            evaluated,
            minimum_score=minimum_score,
        )

        preference_examples = (
            build_preference_examples(
                evaluated,
                minimum_score=minimum_score,
            )
        )

        trajectory_examples = (
            build_trajectory_examples(
                evaluated,
                minimum_score=minimum_score,
            )
        )

        return ExperiencePipelineResult(
            total_experiences=len(evaluated),
            accepted_experiences=len(accepted),
            rejected_experiences=len(rejected),
            sft_examples=sft_examples,
            preference_examples=preference_examples,
            trajectory_examples=trajectory_examples,
        )