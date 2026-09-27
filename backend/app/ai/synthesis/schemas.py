from typing import Any

from pydantic import BaseModel, Field


class SynthesisCandidate(BaseModel):
    provider: str
    model: str
    answer: str

    role: str = "candidate"

    score: float = 0.0
    confidence: float = 0.0

    latency_ms: float | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class SynthesisRequest(BaseModel):
    prompt: str = Field(min_length=1)

    candidates: list[SynthesisCandidate] = Field(
        min_length=1,
        max_length=10,
    )

    synthesis_provider: str | None = None
    synthesis_model: str | None = None

    temperature: float = 0.2

    require_consensus: bool = False

    include_sources: bool = True


class SynthesisResponse(BaseModel):
    answer: str

    candidates_used: int

    selected_candidates: list[str]

    consensus_score: float

    disagreements: list[str] = Field(default_factory=list)

    synthesis_provider: str | None = None
    synthesis_model: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)