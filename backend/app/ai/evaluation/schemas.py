from pydantic import BaseModel, Field


class CandidateAnswer(BaseModel):
    provider: str = Field(min_length=1)
    model: str | None = None
    answer: str = Field(min_length=1, max_length=20000)


class JudgeRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)
    candidates: list[CandidateAnswer] = Field(min_length=1, max_length=5)
    judge_provider: str = Field(default="auto", min_length=1)
    judge_model: str | None = None


class CandidateScore(BaseModel):
    provider: str
    model: str | None = None
    relevance: float
    correctness: float
    completeness: float
    clarity: float
    overall: float
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class JudgeResult(BaseModel):
    winner_provider: str
    winner_model: str | None = None
    confidence: float
    rationale: str
    scores: list[CandidateScore]


class JudgeResponse(BaseModel):
    result: JudgeResult
    judge_provider: str
    judge_model: str | None = None
    evaluation_mode: str