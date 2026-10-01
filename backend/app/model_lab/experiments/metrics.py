from __future__ import annotations


class MetricStore:
    def __init__(self) -> None:
        self._metrics: dict[str, list[float]] = {}

    def add(self, name: str, value: float) -> None:
        self._metrics.setdefault(name, []).append(float(value))

    def latest(self, name: str) -> float | None:
        values = self._metrics.get(name, [])
        return values[-1] if values else None

    def mean(self, name: str) -> float | None:
        values = self._metrics.get(name, [])
        return sum(values) / len(values) if values else None

    def as_dict(self) -> dict[str, list[float]]:
        return {k: list(v) for k, v in self._metrics.items()}