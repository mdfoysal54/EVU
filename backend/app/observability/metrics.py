from dataclasses import dataclass, field
from typing import Any


@dataclass
class Metric:

    name: str

    count: int = 0

    total_time_ms: float = 0.0

    min_time_ms: float | None = None

    max_time_ms: float | None = None

    success_count: int = 0

    failure_count: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def record(
        self,
        duration_ms: float = 0.0,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        self.count += 1

        self.total_time_ms += duration_ms

        if self.min_time_ms is None:

            self.min_time_ms = duration_ms

        else:

            self.min_time_ms = min(
                self.min_time_ms,
                duration_ms,
            )

        if self.max_time_ms is None:

            self.max_time_ms = duration_ms

        else:

            self.max_time_ms = max(
                self.max_time_ms,
                duration_ms,
            )

        if success:

            self.success_count += 1

        else:

            self.failure_count += 1

        if metadata:
            self.metadata.update(
                metadata
            )

    def snapshot(self) -> dict[str, Any]:

        average = (
            self.total_time_ms / self.count
            if self.count
            else 0.0
        )

        return {
            "name": self.name,
            "count": self.count,
            "total_time_ms": round(
                self.total_time_ms,
                2,
            ),
            "average_time_ms": round(
                average,
                2,
            ),
            "min_time_ms": (
                round(
                    self.min_time_ms,
                    2,
                )
                if self.min_time_ms is not None
                else None
            ),
            "max_time_ms": (
                round(
                    self.max_time_ms,
                    2,
                )
                if self.max_time_ms is not None
                else None
            ),
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "metadata": self.metadata,
        }


class MetricsRegistry:

    def __init__(self) -> None:

        self._metrics: dict[
            str,
            Metric,
        ] = {}

    def get_or_create(
        self,
        name: str,
    ) -> Metric:

        if name not in self._metrics:

            self._metrics[name] = Metric(
                name=name
            )

        return self._metrics[name]

    def record(
        self,
        name: str,
        duration_ms: float = 0.0,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        metric = self.get_or_create(
            name
        )

        metric.record(
            duration_ms=duration_ms,
            success=success,
            metadata=metadata,
        )

    def snapshot(self) -> dict[str, Any]:

        return {
            name: metric.snapshot()
            for name, metric
            in self._metrics.items()
        }

    def reset(self) -> None:

        self._metrics.clear()


metrics_registry = MetricsRegistry()