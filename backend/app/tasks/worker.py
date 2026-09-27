from datetime import datetime, timezone

from app.agent.execution.engine import execution_engine
from app.agent.execution.schemas import (
    PlanExecutionRequest,
)
from app.tasks.manager import task_manager
from app.tasks.schemas import TaskStatus


async def run_task(
    task_id: str,
    goal: str,
    max_steps: int,
) -> None:

    task = task_manager.get(task_id)

    if task is None:
        return

    task.status = TaskStatus.RUNNING

    task.started_at = datetime.now(
        timezone.utc
    )

    task_manager.save(task)

    try:

        request = PlanExecutionRequest(
            goal=goal,
            max_steps=max_steps,
            execute=True,
        )

        result = await execution_engine.execute_plan(
            request
        )

        task.result = result.model_dump()

        task.status = TaskStatus.COMPLETED

    except Exception as exc:

        task.status = TaskStatus.FAILED

        task.error = str(exc)

    finally:

        task.completed_at = datetime.now(
            timezone.utc
        )

        task_manager.save(task)