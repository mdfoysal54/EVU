from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    request_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    task_type: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    provider: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    model: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
    )

    latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    input_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    output_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    total_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    estimated_cost: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    error_type: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    judge_relevance: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    judge_correctness: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    judge_completeness: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    judge_clarity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    judge_overall: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    judge_winner: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    request_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
    )

    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    helpful: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    feedback_type: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )