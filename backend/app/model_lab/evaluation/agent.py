from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional
import time


@dataclass
class EvaluationResult:
    name: str
    score: float
    passed: bool
    latency_seconds: float
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def percentage(self) -> float:
        return self.score * 100.0


class AgentEvaluator:
    """
    Generic evaluator for EVU agents/models.

    The evaluator intentionally keeps model execution separate from
    scoring so it can later be connected to different LLM providers,
    local models, or EVU's own inference engine.
    """

    def __init__(
        self,
        threshold: float = 0.5,
        name: str = "agent_evaluation",
    ) -> None:
        self.threshold = threshold
        self.name = name

    def evaluate_case(
        self,
        prompt: str,
        expected: Any,
        runner: Callable[[str], Any],
        scorer: Callable[[Any, Any], float],
    ) -> EvaluationResult:
        started = time.perf_counter()

        try:
            actual = runner(prompt)
            score = float(scorer(actual, expected))
            score = max(0.0, min(1.0, score))

            return EvaluationResult(
                name=self.name,
                score=score,
                passed=score >= self.threshold,
                latency_seconds=time.perf_counter() - started,
                details={
                    "prompt": prompt,
                    "expected": expected,
                    "actual": actual,
                },
            )

        except Exception as exc:
            return EvaluationResult(
                name=self.name,
                score=0.0,
                passed=False,
                latency_seconds=time.perf_counter() - started,
                details={
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )

    def evaluate_batch(
        self,
        cases: Iterable[Dict[str, Any]],
        runner: Callable[[str], Any],
        scorer: Callable[[Any, Any], float],
    ) -> list[EvaluationResult]:
        results: list[EvaluationResult] = []

        for case in cases:
            results.append(
                self.evaluate_case(
                    prompt=case["prompt"],
                    expected=case.get("expected"),
                    runner=runner,
                    scorer=scorer,
                )
            )

        return results

    @staticmethod
    def aggregate(results: Iterable[EvaluationResult]) -> Dict[str, Any]:
        results = list(results)

        if not results:
            return {
                "count": 0,
                "score": 0.0,
                "pass_rate": 0.0,
                "latency_seconds": 0.0,
            }

        return {
            "count": len(results),
            "score": sum(r.score for r in results) / len(results),
            "pass_rate": sum(r.passed for r in results) / len(results),
            "latency_seconds": (
                sum(r.latency_seconds for r in results) / len(results)
            ),
        }