from __future__ import annotations

from .schema import (
    ImprovementCandidate,
    ImprovementConfig,
)


class ExperienceSelector:
    def __init__(
        self,
        config: ImprovementConfig | None = None,
    ) -> None:
        self.config = (
            config
            or ImprovementConfig()
        )

    def select(
        self,
        candidates: list[
            ImprovementCandidate
        ],
    ) -> list[ImprovementCandidate]:
        selected = []

        for candidate in candidates:
            if not candidate.success:
                continue

            if (
                candidate.quality_score
                < self.config.min_quality_score
            ):
                continue

            selected.append(candidate)

        return selected

    def enough_data(
        self,
        selected: list[
            ImprovementCandidate
        ],
    ) -> bool:
        return len(selected) >= (
            self.config.min_examples
        )