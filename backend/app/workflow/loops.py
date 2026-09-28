from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional


@dataclass
class LoopResult:
    iterations: int
    results: list[Any]
    stopped_by_condition: bool
    reached_limit: bool


class LoopController:
    """
    Bounded loop controller.

    This is deliberately separate from the DAG itself.

    The DAG remains acyclic. A loop is represented as repeated
    invocation of a bounded operation rather than introducing
    graph cycles.
    """

    def __init__(
        self,
        max_iterations: int = 100,
    ) -> None:

        if max_iterations < 1:
            raise ValueError(
                "max_iterations must be >= 1"
            )

        self.max_iterations = max_iterations

    async def run(
        self,
        operation: Callable[[int], Any],
        *,
        condition: Optional[
            Callable[[int, Any], bool]
        ] = None,
    ) -> LoopResult:

        results: list[Any] = []

        for index in range(
            self.max_iterations
        ):

            result = operation(index)

            if isinstance(
                result,
                Awaitable,
            ):
                result = await result

            results.append(result)

            if condition is not None:
                should_continue = condition(
                    index,
                    result,
                )

                if not should_continue:
                    return LoopResult(
                        iterations=index + 1,
                        results=results,
                        stopped_by_condition=True,
                        reached_limit=False,
                    )

        return LoopResult(
            iterations=self.max_iterations,
            results=results,
            stopped_by_condition=False,
            reached_limit=True,
        )