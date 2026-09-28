from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


ConditionFunction = Callable[
    [Mapping[str, Any]],
    bool,
]


@dataclass
class Condition:
    """
    Generic workflow condition.
    """

    function: ConditionFunction
    name: str = "condition"

    def evaluate(
        self,
        variables: Mapping[str, Any],
    ) -> bool:

        return bool(
            self.function(variables)
        )


def equals(
    key: str,
    expected: Any,
) -> Condition:

    return Condition(
        name=f"{key} == {expected!r}",
        function=lambda variables: variables.get(key)
        == expected,
    )


def not_equals(
    key: str,
    expected: Any,
) -> Condition:

    return Condition(
        name=f"{key} != {expected!r}",
        function=lambda variables: variables.get(key)
        != expected,
    )


def exists(key: str) -> Condition:
    return Condition(
        name=f"{key} exists",
        function=lambda variables: key in variables,
    )


def truthy(key: str) -> Condition:
    return Condition(
        name=f"{key} truthy",
        function=lambda variables: bool(
            variables.get(key)
        ),
    )


def all_of(
    *conditions: Condition,
) -> Condition:

    return Condition(
        name=" AND ".join(
            condition.name
            for condition in conditions
        ),
        function=lambda variables: all(
            condition.evaluate(variables)
            for condition in conditions
        ),
    )


def any_of(
    *conditions: Condition,
) -> Condition:

    return Condition(
        name=" OR ".join(
            condition.name
            for condition in conditions
        ),
        function=lambda variables: any(
            condition.evaluate(variables)
            for condition in conditions
        ),
    )


def negate(
    condition: Condition,
) -> Condition:

    return Condition(
        name=f"NOT ({condition.name})",
        function=lambda variables: not condition.evaluate(
            variables
        ),
    )