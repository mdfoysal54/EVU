from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class EvaluationCase:
    name: str
    prompt: str
    expected: Any = None
    metadata: dict = field(default_factory=dict)


@dataclass
class EvaluationResult:
    name: str
    score: float
    passed: bool
    output: Any = None
    details: dict = field(default_factory=dict)


class EvaluationSuite:
    def __init__(
        self,
        name: str,
        threshold: float = 0.5,
    ) -> None:
        self.name = name
        self.threshold = threshold
        self.cases: list[EvaluationCase] = []

    def add(
        self,
        case: EvaluationCase,
    ) -> None:
        self.cases.append(case)

    def run(
        self,
        runner: Callable[[str], Any],
        scorer: Callable[
            [EvaluationCase, Any],
            float,
        ],
    ) -> list[EvaluationResult]:
        results = []

        for case in self.cases:
            try:
                output = runner(case.prompt)

                score = float(
                    scorer(case, output)
                )

                score = max(
                    0.0,
                    min(1.0, score),
                )

                results.append(
                    EvaluationResult(
                        name=case.name,
                        score=score,
                        passed=(
                            score
                            >= self.threshold
                        ),
                        output=output,
                    )
                )

            except Exception as exc:
                results.append(
                    EvaluationResult(
                        name=case.name,
                        score=0.0,
                        passed=False,
                        details={
                            "error": str(exc),
                            "error_type": type(
                                exc
                            ).__name__,
                        },
                    )
                )

        return results

    def summary(
        self,
        results: list[EvaluationResult],
    ) -> dict:
        if not results:
            return {
                "suite": self.name,
                "cases": 0,
                "average_score": 0.0,
                "pass_rate": 0.0,
            }

        return {
            "suite": self.name,
            "cases": len(results),
            "average_score": (
                sum(
                    result.score
                    for result in results
                )
                / len(results)
            ),
            "pass_rate": (
                sum(
                    1
                    for result in results
                    if result.passed
                )
                / len(results)
            ),
        }