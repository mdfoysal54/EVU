from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserMemoryCreate(BaseModel):
    category: str = Field(
        default="general",
        min_length=1,
        max_length=80,
    )

    key: str = Field(
        min_length=1,
        max_length=160,
    )

    value: str = Field(
        min_length=1,
        max_length=5000,
    )

    source: str = Field(
        default="explicit",
        min_length=1,
        max_length=80,
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class UserMemoryUpdate(BaseModel):
    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=80,
    )

    key: str | None = Field(
        default=None,
        min_length=1,
        max_length=160,
    )

    value: str | None = Field(
        default=None,
        min_length=1,
        max_length=5000,
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    is_active: bool | None = None


class UserMemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    key: str
    value: str
    source: str
    confidence: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ConversationMemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    summary: str
    message_count: int
    last_summarized_message_id: int | None
    created_at: datetime
    updated_at: datetime


class MemoryContextResponse(BaseModel):
    user_memory: str
    conversation_memory: str