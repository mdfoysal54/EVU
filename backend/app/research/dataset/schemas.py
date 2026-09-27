from datetime import datetime

from pydantic import BaseModel, Field


class DatasetExample(BaseModel):
    request_id: str = Field(min_length=1)

    task_type: str | None = None

    prompt: str = Field(
        min_length=1,
        max_length=20000,
    )

    response: str = Field(
        min_length=1,
        max_length=30000,
    )

    provider: str | None = None
    model: str | None = None

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

    user_rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    user_comment: str | None = None

    created_at: datetime | None = None


class DatasetBuildRequest(BaseModel):
    min_judge_score: float = Field(
        default=7.0,
        ge=0,
        le=10,
    )

    min_user_rating: int = Field(
        default=4,
        ge=1,
        le=5,
    )

    require_judge_score: bool = True

    require_user_feedback: bool = False

    max_examples: int = Field(
        default=1000,
        ge=1,
        le=100000,
    )


class DatasetBuildResponse(BaseModel):
    dataset_version: str

    total_candidates: int
    accepted_examples: int
    rejected_examples: int

    quality_threshold: float

    examples: list[DatasetExample]


class DatasetExportResponse(BaseModel):
    dataset_version: str
    example_count: int
    format: str
    jsonl: str