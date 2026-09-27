import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

from app.tasks.schemas import (
    TaskResponse,
    TaskStatus,
)


class TaskManager:

    def __init__(self) -> None:

        self._tasks: dict[str, TaskResponse] = {}

        self._jobs: dict[
            str,
            asyncio.Task,
        ] = {}

    def create(
        self,
        goal: str,
    ) -> TaskResponse:

        task_id = str(uuid.uuid4())

        task = TaskResponse(
            task_id=task_id,
            status=TaskStatus.QUEUED,
            goal=goal,
            created_at=datetime.now(
                timezone.utc
            ),
        )

        self._tasks[task_id] = task

        return task

    def get(
        self,
        task_id: str,
    ) -> TaskResponse | None:

        return self._tasks.get(task_id)

    def save(
        self,
        task: TaskResponse,
    ) -> None:

        self._tasks[task.task_id] = task

    def attach_job(
        self,
        task_id: str,
        job: asyncio.Task,
    ) -> None:

        self._jobs[task_id] = job

    def cancel(
        self,
        task_id: str,
    ) -> bool:

        job = self._jobs.get(task_id)

        if job is None:
            return False

        if job.done():
            return False

        job.cancel()

        task = self.get(task_id)

        if task:

            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now(
                timezone.utc
            )

        return True

    def list(
        self,
    ) -> list[TaskResponse]:

        return list(
            self._tasks.values()
        )


task_manager = TaskManager()