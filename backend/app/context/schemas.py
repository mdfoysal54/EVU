from pydantic import BaseModel, Field


class ContextNodeCreate(BaseModel):
    uri: str
    context_type: str
    name: str

    content: str = ""

    user_id: int | None = None

    parent_uri: str | None = None

    abstract: str | None = None

    overview: str | None = None

    metadata: dict = Field(default_factory=dict)

    source: str | None = None


class ContextSearchRequest(BaseModel):
    query: str

    user_id: int | None = None

    context_type: str | None = None

    target_uri: str | None = None

    limit: int = Field(
        default=8,
        ge=1,
        le=50,
    )

    max_chars: int | None = None


class ContextResult(BaseModel):
    uri: str
    context_type: str
    name: str
    level: int
    score: float

    abstract: str | None = None
    overview: str | None = None
    content: str | None = None

    match_reason: str | None = None


class ContextSearchResponse(BaseModel):
    results: list[ContextResult]

    query: str
    context_type: str | None = None