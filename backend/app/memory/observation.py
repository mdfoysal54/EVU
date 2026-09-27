from dataclasses import dataclass
from datetime import datetime


@dataclass
class MemoryObservation:
    content: str

    user_id: int | None = None
    project_id: int | None = None
    conversation_id: int | None = None
    session_id: str | None = None
    agent_id: str | None = None

    source: str = "conversation"

    created_at: datetime | None = None

    importance: float = 0.5

    confidence: float = 0.5

    content_hash: str | None = None