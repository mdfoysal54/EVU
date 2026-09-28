from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from .context import PipelineContext


@dataclass
class Stage:
    """
    Base concrete stage.

    Subclasses may override `execute`.
    """

    name: str
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def execute(self, context: PipelineContext) -> Any:
        raise NotImplementedError


@dataclass
class FunctionStage(Stage):
    """
    Stage backed by a normal Python callable.

    Supported callables:

        fn(context)

    or:

        fn(context) -> result
    """

    function: Callable[[PipelineContext], Any] = field(
        default=lambda context: None
    )

    def execute(self, context: PipelineContext) -> Any:
        return self.function(context)


@dataclass
class AsyncFunctionStage(Stage):
    """
    Async stage.

    Runner detects awaitables and executes them through the async runner.
    """

    function: Callable[[PipelineContext], Any] = field(
        default=lambda context: None
    )

    async def execute_async(self, context: PipelineContext) -> Any:
        result = self.function(context)

        if inspect.isawaitable(result):
            return await result

        return result


class TransformStage(FunctionStage):
    """Alias used when a callable transforms context data."""


class ValidationStage(FunctionStage):
    """Alias used for validation-oriented stages."""