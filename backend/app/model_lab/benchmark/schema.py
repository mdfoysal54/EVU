from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BenchmarkCase:
    case_id: str
    category: str
    prompt: str
    expected: Any = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class BenchmarkResult:
    case_id: str
    category: str
    score: float
    passed: bool
    latency_seconds: float
    output: Any = None
    expected: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class BenchmarkReport:
    model_id: str
    model_version: str
    results: list[BenchmarkResult]

    def category_scores(self) -> dict[str, float]:
        grouped: dict[str, list[float]] = {}

        for result in self.results:
            grouped.setdefault(
                result.category,
                [],
            ).append(result.score)

        return {
            category: (
                sum(scores) / len(scores)
                if scores
                else 0.0
            )
            for category, scores
            in grouped.items()
        }

    @property
    def average_score(self) -> float:
        if not self.results:
            return 0.0

        return sum(
            item.score
            for item in self.results
        ) / len(self.results)

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0

        return sum(
            1
            for item in self.results
            if item.passed
        ) / len(self.results)

    @property
    def average_latency(self) -> float:
        if not self.results:
            return 0.0

        return sum(
            item.latency_seconds
            for item in self.results
        ) / len(self.results)

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "model_version": self.model_version,
            "average_score": self.average_score,
            "pass_rate": self.pass_rate,
            "average_latency": (
                self.average_latency
            ),
            "category_scores": (
                self.category_scores()
            ),
            "results": [
                {
                    "case_id": r.case_id,
                    "category": r.category,
                    "score": r.score,
                    "passed": r.passed,
                    "latency_seconds": (
                        r.latency_seconds
                    ),
                    "output": r.output,
                    "expected": r.expected,
                    "error": r.error,
                    "metadata": r.metadata,
                }
                for r in self.results
            ],
        }