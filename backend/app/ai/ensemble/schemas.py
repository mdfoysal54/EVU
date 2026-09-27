from pydantic import BaseModel, Field


class EnsembleRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    provider: str = Field(default="auto", min_length=1)
    model: str | None = None
    max_models: int | None = Field(default=None, ge=1, le=5)
    synthesize: bool = True


class ModelAnswer(BaseModel):
    provider: str
    model: str | None = None
    answer: str
    success: bool = True
    error: str | None = None


class EnsembleResponse(BaseModel):
    response: str
    task: str
    confidence: float
    synthesis_provider: str | None = None
    synthesis_model: str | None = None
    models_consulted: list[ModelAnswer] = Field(default_factory=list)