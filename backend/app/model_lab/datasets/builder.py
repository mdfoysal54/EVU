from __future__ import annotations

from dataclasses import dataclass

from app.model_lab.experience.schema import (
    ExperienceRecord,
)

from .coding import build_coding_dataset
from .reasoning import build_reasoning_dataset
from .tool_use import build_tool_use_dataset


@dataclass
class DatasetBuildResult:

    reasoning: list

    coding: list

    tool_use: list

    @property
    def total(self) -> int:

        return (
            len(self.reasoning)
            + len(self.coding)
            + len(self.tool_use)
        )


def build_specialized_datasets(
    experiences: list[ExperienceRecord],
    minimum_score: float = 0.75,
) -> DatasetBuildResult:

    return DatasetBuildResult(
        reasoning=build_reasoning_dataset(
            experiences,
            minimum_score,
        ),
        coding=build_coding_dataset(
            experiences,
            minimum_score,
        ),
        tool_use=build_tool_use_dataset(
            experiences,
            minimum_score,
        ),
    )