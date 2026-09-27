from datetime import datetime

from pydantic import BaseModel, Field


class TelemetryEventCreate(BaseModel):
    request_id: str = Field(
        min_length=1,
        max_length=64,
    )

    event_type: str = Field(
        default="model_call",
        min_length=1,
        max_length=64,
    )

    task_type: str | None = Field(
        default=None,
        max_length=64,
    )

    provider: str | None = Field(
        default=None,
        max_length=64,
    )

    model: str | None = Field(
        default=None,
        max_length=128,
    )

    success: bool = True

    latency_ms: float | None = Field(
        default=None,
        ge=0,
    )

    input_tokens: int | None = Field(
        default=None,
        ge=0,
    )

    output_tokens: int | None = Field(
        default=None,
        ge=0,
    )

    total_tokens: int | None = Field(
        default=None,
        ge=0,
    )

    estimated_cost: float | None = Field(
        default=None,
        ge=0,
    )

    error_type: str | None = Field(
        default=None,
        max_length=128,
    )

    error_message: str | None = Field(
        default=None,
        max_length=4000,
    )

    judge_relevance: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    judge_correctness: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    judge_completeness: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    judge_clarity: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    judge_overall: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    judge_winner: bool | None = None

    metadata: dict | None = None


class TelemetryEventResponse(BaseModel):
    id: int
    request_id: str
    event_type: str

    task_type: str | None
    provider: str | None
    model: str | None

    success: bool
    latency_ms: float | None

    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None

    estimated_cost: float | None

    judge_overall: float | None
    judge_winner: bool | None

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class ModelPerformance(BaseModel):
    provider: str | None
    model: str | None
    task_type: str | None

    request_count: int
    successful_requests: int
    failed_requests: int

    success_rate: float

    average_latency_ms: float | None

    average_score: float | None
    average_relevance: float | None
    average_correctness: float | None
    average_completeness: float | None
    average_clarity: float | None

    winner_count: int
    winner_rate: float | None

    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int

    estimated_cost: float


class ModelPerformanceResponse(BaseModel):
    window_days: int
    generated_at: datetime
    models: list[ModelPerformance]