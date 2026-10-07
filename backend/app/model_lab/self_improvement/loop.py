from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .collector import (
    extract_candidates,
)
from .dataset_builder import (
    build_sft_dataset,
)
from .evaluator import (
    evaluate_candidate,
)
from .promotion import (
    should_promote,
)
from .schema import (
    ImprovementConfig,
)
from .selector import (
    ExperienceSelector,
)


@dataclass
class ImprovementRun:
    selected_examples: int
    dataset_path: str | None
    training_checkpoint: str | None
    benchmark_score: float
    regression: float
    safety_score: float
    approved: bool
    message: str


class SelfImprovementLoop:
    def __init__(
        self,
        config: ImprovementConfig | None = None,
    ) -> None:
        self.config = (
            config
            or ImprovementConfig()
        )

    def collect_and_select(
        self,
        records: list[dict],
    ):
        candidates = extract_candidates(
            records
        )

        selector = ExperienceSelector(
            self.config
        )

        selected = selector.select(
            candidates
        )

        return selected

    def build_dataset(
        self,
        selected,
        output_path: str,
    ) -> str:
        build_sft_dataset(
            selected,
            output_path,
        )

        return output_path

    def evaluate(
        self,
        *,
        benchmark_score: float,
        regression: float,
        safety_score: float,
    ):
        return evaluate_candidate(
            benchmark_score=(
                benchmark_score
            ),
            regression=regression,
            safety_score=safety_score,
            max_regression=(
                self.config.max_regression
            ),
        )

    def decide(
        self,
        evaluation,
    ):
        return should_promote(
            evaluation,
            allow_auto_promotion=(
                self.config.allow_auto_promotion
            ),
        )