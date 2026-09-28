from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List

from .context import PipelineContext


TransformFunction = Callable[[Any, PipelineContext], Any]


@dataclass
class Transform:
    name: str
    function: TransformFunction

    def apply(
        self,
        value: Any,
        context: PipelineContext,
    ) -> Any:

        return self.function(value, context)


class TransformChain:
    """
    Composable transformation chain.
    """

    def __init__(
        self,
        transforms: Iterable[Transform] = (),
    ) -> None:

        self.transforms: List[Transform] = list(transforms)

    def add(
        self,
        transform: Transform,
    ) -> "TransformChain":

        self.transforms.append(transform)
        return self

    def apply(
        self,
        value: Any,
        context: PipelineContext,
    ) -> Any:

        current = value

        for transform in self.transforms:
            current = transform.apply(
                current,
                context,
            )

        return current


def set_context_value(
    key: str,
) -> Transform:

    def transform(
        value: Any,
        context: PipelineContext,
    ) -> Any:

        context.set(key, value)
        return value

    return Transform(
        name=f"set:{key}",
        function=transform,
    )


def map_dict(
    mapping: Dict[str, str],
) -> Transform:

    def transform(
        value: Any,
        context: PipelineContext,
    ) -> Any:

        if not isinstance(value, dict):
            return value

        return {
            target: value.get(source)
            for target, source in mapping.items()
        }

    return Transform(
        name="map_dict",
        function=transform,
    )


def compose(
    *functions: Callable[[Any], Any],
) -> Transform:

    def transform(
        value: Any,
        context: PipelineContext,
    ) -> Any:

        current = value

        for function in functions:
            current = function(current)

        return current

    return Transform(
        name="compose",
        function=transform,
    )