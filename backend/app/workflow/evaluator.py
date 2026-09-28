from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from .conditions import Condition
from .models import EdgeSpec
from .variables import VariableStore


@dataclass
class ConditionEvaluator:
    """
    Evaluates workflow edge conditions.
    """

    variables: VariableStore

    def evaluate(
        self,
        condition: Any,
    ) -> bool:

        if condition is None:
            return True

        if isinstance(condition, Condition):
            return condition.evaluate(
                self.variables.all()
            )

        if callable(condition):
            return bool(
                condition(
                    self.variables.all()
                )
            )

        if isinstance(condition, bool):
            return condition

        return bool(condition)

    def edge_enabled(
        self,
        edge: EdgeSpec,
    ) -> bool:

        return self.evaluate(
            edge.condition
        )

    def select_edges(
        self,
        edges: list[EdgeSpec],
    ) -> list[EdgeSpec]:

        return [
            edge
            for edge in edges
            if self.edge_enabled(edge)
        ]