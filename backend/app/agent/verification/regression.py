from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable


@dataclass
class RegressionCase:
    case_id: str
    input: Any
    expected: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegressionResult:
    case_id: str
    passed: bool
    actual: Any = None
    expected: Any = None
    error: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RegressionRunner:
    def __init__(
        self,
        comparator: Callable[[Any, Any], bool] | None = None,
    ) -> None:
        self.comparator = comparator or self._default_compare

    def run(
        self,
        cases: Iterable[RegressionCase],
        executor: Callable[[Any], Any],
    ) -> list[RegressionResult]:
        results: list[RegressionResult] = []

        for case in cases:
            try:
                actual = executor(case.input)

                passed = bool(
                    self.comparator(
                        actual,
                        case.expected,
                    )
                )

                results.append(
                    RegressionResult(
                        case_id=case.case_id,
                        passed=passed,
                        actual=actual,
                        expected=case.expected,
                        metadata=dict(case.metadata),
                    )
                )

            except Exception as exc:
                results.append(
                    RegressionResult(
                        case_id=case.case_id,
                        passed=False,
                        expected=case.expected,
                        error=str(exc),
                        metadata=dict(case.metadata),
                    )
                )

        return results

    @staticmethod
    def _default_compare(
        actual: Any,
        expected: Any,
    ) -> bool:
        return actual == expected

    @staticmethod
    def summarize(
        results: Iterable[RegressionResult],
    ) -> Dict[str, Any]:
        results = list(results)

        if not results:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
            }

        passed = sum(
            result.passed
            for result in results
        )

        return {
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "pass_rate": passed / len(results),
        }