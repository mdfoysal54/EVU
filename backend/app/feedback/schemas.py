from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    request_id: str = Field(
        min_length=1,
        max_length=64,
    )

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    helpful: bool | None = None

    feedback_type: str | None = Field(
        default=None,
        max_length=64,
    )

    comment: str | None = Field(
        default=None,
        max_length=4000,
    )


class FeedbackResponse(BaseModel):
    id: int

    request_id: str

    rating: int | None

    helpful: bool | None

    feedback_type: str | None

    comment: str | None

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }