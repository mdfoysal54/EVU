from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional


@dataclass
class Assertion:
    name: str
    predicate: Callable[[Any], bool]
    message: str = ""


@dataclass
class AssertionResult:
    name: str
    passed: bool
    message: str = ""


class AssertionEngine:
    def __init__(
        self,
        assertions: Optional[Iterable[Assertion]] = None,
    ) -> None:
        self.assertions = list(assertions or [])

    def add(self, assertion: Assertion) -> None:
        self.assertions.append(assertion)

    def evaluate(
        self,
        value: Any,
    ) -> list[AssertionResult]:
        results: list[AssertionResult] = []

        for assertion in self.assertions:
            try:
                passed = bool(
                    assertion.predicate(value)
                )

                results.append(
                    AssertionResult(
                        name=assertion.name,
                        passed=passed,
                        message=(
                            ""
                            if passed
                            else assertion.message
                        ),
                    )
                )

            except Exception as exc:
                results.append(
                    AssertionResult(
                        name=assertion.name,
                        passed=False,
                        message=str(exc),
                    )
                )

        return results

    def passed(
        self,
        value: Any,
    ) -> bool:
        results = self.evaluate(value)
        return bool(results) and all(
            result.passed
            for result in results
        )