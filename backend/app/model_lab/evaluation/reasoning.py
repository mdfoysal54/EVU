from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict


@dataclass
class ReasoningEvaluationResult:
    passed: bool
    score: float
    answer: Any = None
    expected: Any = None
    details: Dict[str, Any] = field(default_factory=dict)


class ReasoningEvaluator:
    """
    Evaluation helpers for reasoning-style tasks.

    Scoring can be exact, custom, or rubric-based.
    """

    def __init__(
        self,
        threshold: float = 0.5,
    ) -> None:
        self.threshold = threshold

    def evaluate(
        self,
        answer: Any,
        expected: Any,
        scorer: Callable[[Any, Any], float],
    ) -> ReasoningEvaluationResult:
        try:
            score = float(scorer(answer, expected))
            score = max(0.0, min(1.0, score))

            return ReasoningEvaluationResult(
                passed=score >= self.threshold,
                score=score,
                answer=answer,
                expected=expected,
            )

        except Exception as exc:
            return ReasoningEvaluationResult(
                passed=False,
                score=0.0,
                answer=answer,
                expected=expected,
                details={
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )

    def exact_match(
        self,
        answer: Any,
        expected: Any,
    ) -> ReasoningEvaluationResult:
        normalized_answer = str(answer).strip().lower()
        normalized_expected = str(expected).strip().lower()

        passed = normalized_answer == normalized_expected

        return ReasoningEvaluationResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            answer=answer,
            expected=expected,
        )

    @staticmethod
    def keyword_score(
        answer: str,
        keywords: list[str],
    ) -> float:
        if not keywords:
            return 0.0

        text = answer.lower()

        matches = sum(
            1
            for keyword in keywords
            if keyword.lower() in text
        )

        return matches / len(keywords)