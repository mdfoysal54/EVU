from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Checkpoint:
    id: str
    pipeline_id: str
    execution_id: str

    stage_name: Optional[str]

    context: Dict[str, Any]

    created_at: datetime


class CheckpointStore:
    """
    Default in-memory checkpoint store.

    EVU can later replace this with PostgreSQL/Redis/object storage
    without changing pipeline execution logic.
    """

    def __init__(self) -> None:
        self._items: Dict[str, Checkpoint] = {}

    def save(
        self,
        checkpoint_id: str,
        pipeline_id: str,
        execution_id: str,
        stage_name: Optional[str],
        context: Dict[str, Any],
    ) -> Checkpoint:

        checkpoint = Checkpoint(
            id=checkpoint_id,
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            stage_name=stage_name,
            context=copy.deepcopy(context),
            created_at=_now(),
        )

        self._items[checkpoint_id] = checkpoint
        return checkpoint

    def get(self, checkpoint_id: str) -> Optional[Checkpoint]:
        return self._items.get(checkpoint_id)

    def delete(self, checkpoint_id: str) -> None:
        self._items.pop(checkpoint_id, None)

    def list_execution(
        self,
        execution_id: str,
    ) -> List[Checkpoint]:
        return [
            item
            for item in self._items.values()
            if item.execution_id == execution_id
        ]

    def latest(
        self,
        execution_id: str,
    ) -> Optional[Checkpoint]:

        items = self.list_execution(execution_id)

        if not items:
            return None

        return max(
            items,
            key=lambda item: item.created_at,
        )

    def clear(self) -> None:
        self._items.clear()