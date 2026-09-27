import asyncio

from app.tasks.manager import task_manager
from app.tasks.schemas import (
    TaskCreateRequest,
    TaskResponse,
)
from app.tasks.worker import run_task


class TaskService:

    async def create(
        self,
        request: TaskCreateRequest,
    ) -> TaskResponse:

        task = task_manager.create(
            goal=request.goal
        )

        job = asyncio.create_task(
            run_task(
                task_id=task.task_id,
                goal=request.goal,
                max_steps=request.max_steps,
            )
        )

        task_manager.attach_job(
            task.task_id,
            job,
        )

        return task

    def get(
        self,
        task_id: str,
    ) -> TaskResponse | None:

        return task_manager.get(task_id)

    def cancel(
        self,
        task_id: str,
    ) -> bool:

        return task_manager.cancel(
            task_id
        )

    def list(
        self,
    ) -> list[TaskResponse]:

        return task_manager.list()


task_service = TaskService()