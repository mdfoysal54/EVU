from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PlanStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStep(BaseModel):
    id: int

    title: str

    description: str

    action: str = "reason"

    tool: str | None = None

    depends_on: list[int] = Field(
        default_factory=list
    )

    status: PlanStepStatus = PlanStepStatus.PENDING

    result: Any | None = None

    error: str | None = None


class AgentPlan(BaseModel):
    goal: str

    steps: list[PlanStep]

    max_steps: int = 8

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class PlanningRequest(BaseModel):
    goal: str = Field(min_length=1)

    max_steps: int = Field(
        default=8,
        ge=1,
        le=20,
    )

    execute: bool = False


class PlanningResponse(BaseModel):
    goal: str

    plan: AgentPlan

    execution_results: list[dict[str, Any]] = Field(
        default_factory=list
    )