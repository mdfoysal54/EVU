from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ContextNode(Base):
    __tablename__ = "context_nodes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    uri: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        index=True,
    )

    parent_uri: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        index=True,
    )

    context_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
    )

    is_leaf: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    abstract: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    overview: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    metadata_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    embedding_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "uri",
            name="uq_context_user_uri",
        ),
    )