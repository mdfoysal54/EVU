from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional

from .assertions import Assertion, AssertionEngine


@dataclass
class VerificationResult:
    passed: bool
    score: float
    checks: list[Dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class Verifier:
    def __init__(
        self,
        assertions: Optional[Iterable[Assertion]] = None,
    ) -> None:
        self.engine = AssertionEngine(assertions)

    def add_assertion(
        self,
        assertion: Assertion,
    ) -> None:
        self.engine.add(assertion)

    def verify(
        self,
        value: Any,
    ) -> VerificationResult:
        results = self.engine.evaluate(value)

        if not results:
            return VerificationResult(
                passed=True,
                score=1.0,
                checks=[],
            )

        passed_count = sum(
            result.passed
            for result in results
        )

        score = passed_count / len(results)

        return VerificationResult(
            passed=passed_count == len(results),
            score=score,
            checks=[
                {
                    "name": result.name,
                    "passed": result.passed,
                    "message": result.message,
                }
                for result in results
            ],
        )

    def verify_with(
        self,
        value: Any,
        checks: Iterable[
            Callable[[Any], bool]
        ],
    ) -> VerificationResult:
        results: list[bool] = []
        errors: list[str] = []

        for check in checks:
            try:
                results.append(bool(check(value)))
            except Exception as exc:
                results.append(False)
                errors.append(str(exc))

        if not results:
            return VerificationResult(
                passed=True,
                score=1.0,
                errors=errors,
            )

        score = sum(results) / len(results)

        return VerificationResult(
            passed=all(results),
            score=score,
            errors=errors,
        )