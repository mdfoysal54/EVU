from pydantic import BaseModel, Field


class OrchestrationRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    provider: str = Field(default="auto", min_length=1)
    model: str | None = None
    conversation_id: int | None = None
    use_rag: bool = True


class RoutingInfo(BaseModel):
    provider: str
    model: str | None = None
    task: str
    confidence: float
    reason: str
    candidates: list[dict]


class OrchestrationResponse(BaseModel):
    response: str
    provider: str
    model: str | None = None
    task: str
    routing: RoutingInfo