from __future__ import annotations

import time
from collections.abc import Callable

from .schema import (
    BenchmarkCase,
    BenchmarkResult,
)


class BenchmarkRunner:
    def __init__(
        self,
        threshold: float = 0.5,
    ) -> None:
        self.threshold = threshold

    def run(
        self,
        cases: list[BenchmarkCase],
        generator: Callable[[str], str],
        scorer: Callable[[object, object], float],
    ) -> list[BenchmarkResult]:
        results = []

        for case in cases:
            started = time.perf_counter()

            try:
                output = generator(
                    case.prompt
                )

                score = float(
                    scorer(
                        output,
                        case.expected,
                    )
                )

                score = max(
                    0.0,
                    min(1.0, score),
                )

                results.append(
                    BenchmarkResult(
                        case_id=case.case_id,
                        category=case.category,
                        score=score,
                        passed=(
                            score
                            >= self.threshold
                        ),
                        latency_seconds=(
                            time.perf_counter()
                            - started
                        ),
                        output=output,
                        expected=case.expected,
                        metadata=dict(
                            case.metadata
                        ),
                    )
                )

            except Exception as exc:
                results.append(
                    BenchmarkResult(
                        case_id=case.case_id,
                        category=case.category,
                        score=0.0,
                        passed=False,
                        latency_seconds=(
                            time.perf_counter()
                            - started
                        ),
                        expected=case.expected,
                        error=str(exc),
                        metadata={
                            **case.metadata,
                            "error_type": (
                                type(exc).__name__
                            ),
                        },
                    )
                )

        return results