from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class WorkflowCheckpoint:
    id: str
    workflow_id: str
    execution_id: str

    state: Dict[str, Any]

    created_at: datetime = field(
        default_factory=utc_now
    )


class WorkflowCheckpointStore:
    """
    In-memory workflow checkpoint store.

    Replaceable later with Redis/PostgreSQL/object storage.
    """

    def __init__(self) -> None:
        self._items: Dict[
            str,
            WorkflowCheckpoint,
        ] = {}

    def save(
        self,
        checkpoint_id: str,
        workflow_id: str,
        execution_id: str,
        state: Dict[str, Any],
    ) -> WorkflowCheckpoint:

        checkpoint = WorkflowCheckpoint(
            id=checkpoint_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            state=copy.deepcopy(state),
        )

        self._items[checkpoint_id] = checkpoint

        return checkpoint

    def get(
        self,
        checkpoint_id: str,
    ) -> Optional[WorkflowCheckpoint]:

        return self._items.get(
            checkpoint_id
        )

    def list_execution(
        self,
        execution_id: str,
    ) -> List[WorkflowCheckpoint]:

        return [
            item
            for item in self._items.values()
            if item.execution_id == execution_id
        ]

    def latest(
        self,
        execution_id: str,
    ) -> Optional[WorkflowCheckpoint]:

        items = self.list_execution(
            execution_id
        )

        if not items:
            return None

        return max(
            items,
            key=lambda item: item.created_at,
        )

    def delete(
        self,
        checkpoint_id: str,
    ) -> None:

        self._items.pop(
            checkpoint_id,
            None,
        )