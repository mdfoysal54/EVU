from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ProvenanceEvent:
    event_type: str
    pipeline_id: str
    execution_id: str

    stage_name: Optional[str] = None

    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class ProvenanceTracker:
    """
    Records execution lineage.

    This is deliberately generic so it can later feed EVU telemetry,
    observability, auditing and evaluation systems.
    """

    def __init__(self) -> None:
        self.events: List[ProvenanceEvent] = []

    def record(
        self,
        event_type: str,
        pipeline_id: str,
        execution_id: str,
        stage_name: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProvenanceEvent:

        event = ProvenanceEvent(
            event_type=event_type,
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            stage_name=stage_name,
            input_data=input_data or {},
            output_data=output_data or {},
            metadata=metadata or {},
        )

        self.events.append(event)
        return event

    def stage_started(
        self,
        pipeline_id: str,
        execution_id: str,
        stage_name: str,
        **metadata: Any,
    ) -> ProvenanceEvent:

        return self.record(
            "stage.started",
            pipeline_id,
            execution_id,
            stage_name,
            metadata=metadata,
        )

    def stage_completed(
        self,
        pipeline_id: str,
        execution_id: str,
        stage_name: str,
        output: Any = None,
        **metadata: Any,
    ) -> ProvenanceEvent:

        return self.record(
            "stage.completed",
            pipeline_id,
            execution_id,
            stage_name,
            output_data={"result": output},
            metadata=metadata,
        )

    def stage_failed(
        self,
        pipeline_id: str,
        execution_id: str,
        stage_name: str,
        error: str,
        **metadata: Any,
    ) -> ProvenanceEvent:

        return self.record(
            "stage.failed",
            pipeline_id,
            execution_id,
            stage_name,
            metadata={
                **metadata,
                "error": error,
            },
        )

    def export(self) -> List[Dict[str, Any]]:
        return [event.to_dict() for event in self.events]

    def clear(self) -> None:
        self.events.clear()