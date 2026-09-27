from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RoutingPolicy:

    prefer_local: bool = False

    privacy_sensitive: bool = False

    latency_sensitive: bool = False

    quality_priority: float = 0.7

    cost_priority: float = 0.1

    latency_priority: float = 0.1

    privacy_priority: float = 0.1

    minimum_quality: float = 0.0

    allow_external: bool = True

    allow_local: bool = True

    explicit_provider: str | None = None

    explicit_model: str | None = None