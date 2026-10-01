from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterable


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class HealthStatus:
    name: str
    healthy: bool
    latency_ms: float | None = None
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "healthy": self.healthy,
            "latency_ms": self.latency_ms,
            "message": self.message,
            "details": self.details,
            "checked_at": self.checked_at.isoformat(),
        }


class IntegrationHealthRegistry:
    def __init__(self) -> None:
        self._checks: dict[str, Callable[[], Any]] = {}

    def register(self, name: str, check: Callable[[], Any]) -> None:
        self._checks[name] = check

    def check(self, name: str) -> HealthStatus:
        if name not in self._checks:
            return HealthStatus(name, False, message="Unknown integration")
        start = datetime.now(timezone.utc)
        try:
            result = self._checks[name]()
            healthy = bool(result) if isinstance(result, bool) else True
            details = result if isinstance(result, dict) else {}
            latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return HealthStatus(name, healthy, latency, "ok" if healthy else "unhealthy", details)
        except Exception as exc:
            latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return HealthStatus(name, False, latency, str(exc))

    def check_all(self) -> list[HealthStatus]:
        return [self.check(name) for name in self._checks]

    def healthy(self) -> bool:
        return all(status.healthy for status in self.check_all())


health_registry = IntegrationHealthRegistry()
