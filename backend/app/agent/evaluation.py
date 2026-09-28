from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable


@dataclass
class AgentEvaluation:
    agent_id: str

    score: float
    passed: bool

    task: str = ""

    metrics: Dict[str, float] = field(
        default_factory=dict
    )

    details: Dict[str, Any] = field(
        default_factory=dict
    )


class AgentEvaluator:
    def __init__(
        self,
        threshold: float = 0.5,
    ) -> None:
        self.threshold = threshold

    def evaluate(
        self,
        agent_id: str,
        task: str,
        actual: Any,
        expected: Any,
        scorer: Callable[[Any, Any], float],
        metrics: Dict[str, float] | None = None,
    ) -> AgentEvaluation:
        try:
            score = float(
                scorer(actual, expected)
            )

            score = max(
                0.0,
                min(1.0, score),
            )

            return AgentEvaluation(
                agent_id=agent_id,
                task=task,
                score=score,
                passed=score >= self.threshold,
                metrics=dict(metrics or {}),
                details={
                    "actual": actual,
                    "expected": expected,
                },
            )

        except Exception as exc:
            return AgentEvaluation(
                agent_id=agent_id,
                task=task,
                score=0.0,
                passed=False,
                metrics=dict(metrics or {}),
                details={
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )

    @staticmethod
    def aggregate(
        evaluations: Iterable[AgentEvaluation],
    ) -> Dict[str, Any]:
        evaluations = list(evaluations)

        if not evaluations:
            return {
                "count": 0,
                "average_score": 0.0,
                "pass_rate": 0.0,
            }

        return {
            "count": len(evaluations),
            "average_score": (
                sum(item.score for item in evaluations)
                / len(evaluations)
            ),
            "pass_rate": (
                sum(item.passed for item in evaluations)
                / len(evaluations)
            ),
        }