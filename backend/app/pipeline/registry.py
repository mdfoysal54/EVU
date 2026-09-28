from __future__ import annotations

from threading import RLock
from typing import Dict, Iterable, Optional

from .base import Pipeline


class PipelineRegistry:
    """
    Central registry for reusable pipelines.

    The registry is intentionally independent from FastAPI and databases.
    """

    def __init__(self) -> None:
        self._pipelines: Dict[str, Pipeline] = {}
        self._lock = RLock()

    def register(
        self,
        pipeline: Pipeline,
        *,
        replace: bool = False,
    ) -> Pipeline:

        pipeline.validate()

        with self._lock:
            if (
                pipeline.name in self._pipelines
                and not replace
            ):
                raise ValueError(
                    f"Pipeline already registered: "
                    f"{pipeline.name}"
                )

            self._pipelines[pipeline.name] = pipeline

        return pipeline

    def get(
        self,
        name: str,
    ) -> Optional[Pipeline]:

        with self._lock:
            return self._pipelines.get(name)

    def require(
        self,
        name: str,
    ) -> Pipeline:

        pipeline = self.get(name)

        if pipeline is None:
            raise KeyError(
                f"Pipeline not registered: {name}"
            )

        return pipeline

    def remove(self, name: str) -> None:
        with self._lock:
            self._pipelines.pop(name, None)

    def names(self) -> Iterable[str]:
        with self._lock:
            return tuple(self._pipelines.keys())

    def clear(self) -> None:
        with self._lock:
            self._pipelines.clear()


registry = PipelineRegistry()