from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional
import time


@dataclass
class BenchmarkCase:
    case_id: str
    prompt: str
    expected: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    case_id: str
    score: float
    passed: bool
    latency_seconds: float
    actual: Any = None
    expected: Any = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkSuite:
    name: str
    cases: list[BenchmarkCase] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add(self, case: BenchmarkCase) -> None:
        self.cases.append(case)

    def __len__(self) -> int:
        return len(self.cases)


class BenchmarkRunner:
    def __init__(
        self,
        threshold: float = 0.5,
    ) -> None:
        self.threshold = threshold

    def run(
        self,
        suite: BenchmarkSuite,
        runner: Callable[[str], Any],
        scorer: Callable[[Any, Any], float],
    ) -> list[BenchmarkResult]:
        results: list[BenchmarkResult] = []

        for case in suite.cases:
            started = time.perf_counter()

            try:
                actual = runner(case.prompt)
                score = float(scorer(actual, case.expected))
                score = max(0.0, min(1.0, score))

                results.append(
                    BenchmarkResult(
                        case_id=case.case_id,
                        score=score,
                        passed=score >= self.threshold,
                        latency_seconds=time.perf_counter() - started,
                        actual=actual,
                        expected=case.expected,
                        details=dict(case.metadata),
                    )
                )

            except Exception as exc:
                results.append(
                    BenchmarkResult(
                        case_id=case.case_id,
                        score=0.0,
                        passed=False,
                        latency_seconds=time.perf_counter() - started,
                        expected=case.expected,
                        details={
                            **case.metadata,
                            "error": str(exc),
                            "error_type": type(exc).__name__,
                        },
                    )
                )

        return results

    @staticmethod
    def summarize(
        results: Iterable[BenchmarkResult],
    ) -> Dict[str, Any]:
        results = list(results)

        if not results:
            return {
                "count": 0,
                "average_score": 0.0,
                "pass_rate": 0.0,
                "average_latency": 0.0,
            }

        return {
            "count": len(results),
            "average_score": sum(r.score for r in results) / len(results),
            "pass_rate": sum(r.passed for r in results) / len(results),
            "average_latency": (
                sum(r.latency_seconds for r in results) / len(results)
            ),
        }