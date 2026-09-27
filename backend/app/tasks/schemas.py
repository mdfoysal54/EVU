from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskCreateRequest(BaseModel):
    goal: str = Field(min_length=1)

    max_steps: int = Field(
        default=8,
        ge=1,
        le=20,
    )


class TaskResponse(BaseModel):
    task_id: str

    status: TaskStatus

    goal: str

    created_at: datetime

    started_at: datetime | None = None

    completed_at: datetime | None = None

    result: Any | None = None

    error: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )