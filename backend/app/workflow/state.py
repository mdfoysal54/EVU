from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .models import NodeStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class NodeState:
    node_id: str

    status: NodeStatus = NodeStatus.PENDING

    result: Any = None
    error: Optional[str] = None

    attempts: int = 0

    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class WorkflowState:
    workflow_id: str
    execution_id: str

    variables: Dict[str, Any] = field(
        default_factory=dict
    )

    nodes: Dict[str, NodeState] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    cancelled: bool = False

    started_at: datetime = field(
        default_factory=utc_now
    )

    finished_at: Optional[datetime] = None

    def node(
        self,
        node_id: str,
    ) -> NodeState:

        if node_id not in self.nodes:
            self.nodes[node_id] = NodeState(
                node_id=node_id
            )

        return self.nodes[node_id]

    def mark_running(
        self,
        node_id: str,
    ) -> None:

        state = self.node(node_id)

        state.status = NodeStatus.RUNNING
        state.started_at = utc_now()
        state.attempts += 1

    def mark_success(
        self,
        node_id: str,
        result: Any = None,
    ) -> None:

        state = self.node(node_id)

        state.status = NodeStatus.SUCCESS
        state.result = result
        state.finished_at = utc_now()

    def mark_failed(
        self,
        node_id: str,
        error: str,
    ) -> None:

        state = self.node(node_id)

        state.status = NodeStatus.FAILED
        state.error = error
        state.finished_at = utc_now()

    def mark_skipped(
        self,
        node_id: str,
    ) -> None:

        state = self.node(node_id)
        state.status = NodeStatus.SKIPPED
        state.finished_at = utc_now()

    def is_complete(self) -> bool:
        return all(
            state.status in {
                NodeStatus.SUCCESS,
                NodeStatus.SKIPPED,
            }
            for state in self.nodes.values()
        )

    def snapshot(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "variables": dict(self.variables),
            "nodes": {
                node_id: {
                    "status": state.status.value,
                    "result": state.result,
                    "error": state.error,
                    "attempts": state.attempts,
                    "metadata": dict(state.metadata),
                }
                for node_id, state in self.nodes.items()
            },
            "metadata": dict(self.metadata),
            "cancelled": self.cancelled,
            "started_at": self.started_at.isoformat(),
            "finished_at": (
                self.finished_at.isoformat()
                if self.finished_at
                else None
            ),
        }