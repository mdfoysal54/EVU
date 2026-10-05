from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ExperienceEvent:
    """
    Atomic event emitted by the EVU runtime.

    Examples:

    - request_started
    - model_started
    - model_completed
    - tool_started
    - tool_completed
    - tool_failed
    - observation
    - response
    - request_completed
    - request_failed
    """

    event_id: str
    experience_id: str
    event_type: str
    timestamp: str = field(default_factory=utc_now)

    step_id: int | None = None

    name: str | None = None

    input_data: Any = None
    output_data: Any = None

    success: bool | None = None

    latency_ms: float | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)