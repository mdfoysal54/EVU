from __future__ import annotations

from dataclasses import dataclass

from .schema import BenchmarkReport


@dataclass
class RegressionResult:
    acceptable: bool
    overall_delta: float
    category_deltas: dict[str, float]
    regressions: dict[str, float]
    improvements: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "acceptable": self.acceptable,
            "overall_delta": self.overall_delta,
            "category_deltas": (
                self.category_deltas
            ),
            "regressions": self.regressions,
            "improvements": self.improvements,
        }


def compare_reports(
    current: BenchmarkReport,
    candidate: BenchmarkReport,
    *,
    max_overall_drop: float = 0.02,
    max_category_drop: float = 0.05,
) -> RegressionResult:
    current_categories = (
        current.category_scores()
    )

    candidate_categories = (
        candidate.category_scores()
    )

    all_categories = (
        set(current_categories)
        | set(candidate_categories)
    )

    deltas: dict[str, float] = {}
    regressions: dict[str, float] = {}
    improvements: dict[str, float] = {}

    for category in all_categories:
        old = current_categories.get(
            category,
            0.0,
        )

        new = candidate_categories.get(
            category,
            0.0,
        )

        delta = new - old

        deltas[category] = delta

        if delta < -max_category_drop:
            regressions[category] = delta

        elif delta > 0:
            improvements[category] = delta

    overall_delta = (
        candidate.average_score
        - current.average_score
    )

    acceptable = (
        overall_delta
        >= -max_overall_drop
        and not regressions
    )

    return RegressionResult(
        acceptable=acceptable,
        overall_delta=overall_delta,
        category_deltas=deltas,
        regressions=regressions,
        improvements=improvements,
    )