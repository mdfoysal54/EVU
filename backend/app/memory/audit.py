from dataclasses import dataclass
from datetime import datetime


@dataclass
class MemoryAuditEvent:
    action: str
    memory_id: int | None
    actor_id: int | None
    reason: str | None
    created_at: datetime