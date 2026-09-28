from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable, List


@dataclass
class ParallelResult:
    results: List[Any]
    errors: List[BaseException]

    @property
    def success(self) -> bool:
        return not self.errors


class ParallelExecutor:
    """
    Runs independent workflow tasks concurrently.
    """

    async def run(
        self,
        functions: Iterable[
            Callable[[], Any]
        ],
        *,
        fail_fast: bool = False,
    ) -> ParallelResult:

        async def invoke(
            function: Callable[[], Any],
        ) -> Any:

            result = function()

            if isinstance(
                result,
                Awaitable,
            ):
                return await result

            return result

        tasks = [
            asyncio.create_task(
                invoke(function)
            )
            for function in functions
        ]

        if fail_fast:
            results: List[Any] = []

            try:
                values = await asyncio.gather(
                    *tasks
                )
                results.extend(values)

                return ParallelResult(
                    results=results,
                    errors=[],
                )

            except Exception as exc:
                for task in tasks:
                    if not task.done():
                        task.cancel()

                return ParallelResult(
                    results=[],
                    errors=[exc],
                )

        values = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        results = []
        errors = []

        for value in values:
            if isinstance(
                value,
                BaseException,
            ):
                errors.append(value)
            else:
                results.append(value)

        return ParallelResult(
            results=results,
            errors=errors,
        )