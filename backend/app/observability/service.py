import time
from contextlib import asynccontextmanager
from typing import Any

from app.observability.logger import (
    get_logger,
)
from app.observability.metrics import (
    metrics_registry,
)


class ObservabilityService:

    def __init__(self) -> None:

        self.logger = get_logger(
            "observability"
        )

    @asynccontextmanager
    async def measure(
        self,
        metric_name: str,
        metadata: dict[str, Any] | None = None,
    ):

        started = time.perf_counter()

        success = False

        try:

            yield

            success = True

        except Exception:

            success = False

            raise

        finally:

            duration_ms = (
                time.perf_counter()
                - started
            ) * 1000

            metrics_registry.record(
                name=metric_name,
                duration_ms=duration_ms,
                success=success,
                metadata=metadata,
            )

    def record(
        self,
        metric_name: str,
        duration_ms: float = 0.0,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        metrics_registry.record(
            name=metric_name,
            duration_ms=duration_ms,
            success=success,
            metadata=metadata,
        )

    def snapshot(
        self,
    ) -> dict[str, Any]:

        return metrics_registry.snapshot()

    def reset(self) -> None:

        metrics_registry.reset()


observability_service = (
    ObservabilityService()
)