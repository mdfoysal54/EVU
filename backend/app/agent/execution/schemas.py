from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolExecutionRequest(BaseModel):
    tool_name: str = Field(min_length=1)

    arguments: dict[str, Any] = Field(
        default_factory=dict
    )


class ToolExecutionResult(BaseModel):
    tool_name: str

    status: ExecutionStatus

    result: Any | None = None

    error: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class PlanExecutionRequest(BaseModel):
    goal: str = Field(min_length=1)

    max_steps: int = Field(
        default=8,
        ge=1,
        le=20,
    )

    execute: bool = True


class PlanExecutionResponse(BaseModel):
    goal: str

    status: ExecutionStatus

    plan: dict[str, Any]

    results: list[dict[str, Any]] = Field(
        default_factory=list
    )