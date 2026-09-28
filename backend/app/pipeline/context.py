from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class PipelineContext:
    """
    Runtime context shared by all pipeline stages.

    The context intentionally contains generic data only. EVU's AI,
    database, memory and tool layers can place their own objects inside
    `data` without coupling the pipeline engine to those systems.
    """

    pipeline_id: str
    execution_id: str = field(default_factory=lambda: str(uuid4()))

    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    current_stage: Optional[str] = None
    cancelled: bool = False

    started_at: datetime = field(default_factory=utc_now)
    finished_at: Optional[datetime] = None

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def update(self, values: Dict[str, Any]) -> None:
        self.data.update(values)

    def has(self, key: str) -> bool:
        return key in self.data

    def delete(self, key: str) -> None:
        self.data.pop(key, None)

    def cancel(self) -> None:
        self.cancelled = True

    def finish(self) -> None:
        self.finished_at = utc_now()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "execution_id": self.execution_id,
            "data": dict(self.data),
            "metadata": dict(self.metadata),
            "current_stage": self.current_stage,
            "cancelled": self.cancelled,
            "started_at": self.started_at.isoformat(),
            "finished_at": (
                self.finished_at.isoformat()
                if self.finished_at
                else None
            ),
        }

    @classmethod
    def from_snapshot(cls, snapshot: Dict[str, Any]) -> "PipelineContext":
        context = cls(
            pipeline_id=snapshot["pipeline_id"],
            execution_id=snapshot["execution_id"],
            data=dict(snapshot.get("data", {})),
            metadata=dict(snapshot.get("metadata", {})),
        )

        context.current_stage = snapshot.get("current_stage")
        context.cancelled = bool(snapshot.get("cancelled", False))

        if snapshot.get("started_at"):
            context.started_at = datetime.fromisoformat(
                snapshot["started_at"]
            )

        if snapshot.get("finished_at"):
            context.finished_at = datetime.fromisoformat(
                snapshot["finished_at"]
            )

        return context