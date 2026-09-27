from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class UserMemory(Base):
    __tablename__ = "user_memories"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "category",
            "key",
            name="uq_user_memory_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(80),
        index=True,
    )

    key: Mapped[str] = mapped_column(
        String(160),
    )

    value: Mapped[str] = mapped_column(
        Text,
    )

    source: Mapped[str] = mapped_column(
        String(80),
        default="explicit",
    )

    confidence: Mapped[float] = mapped_column(
        default=1.0,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class ConversationMemory(Base):
    __tablename__ = "conversation_memories"

    __table_args__ = (
        UniqueConstraint(
            "conversation_id",
            name="uq_conversation_memory",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"),
        index=True,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    message_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    last_summarized_message_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )