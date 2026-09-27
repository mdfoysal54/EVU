from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MetricSnapshot(BaseModel):

    name: str

    count: int = 0

    total_time_ms: float = 0.0

    min_time_ms: float | None = None

    max_time_ms: float | None = None

    success_count: int = 0

    failure_count: int = 0

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ObservationEvent(BaseModel):

    event_type: str

    timestamp: datetime

    duration_ms: float | None = None

    success: bool = True

    name: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )