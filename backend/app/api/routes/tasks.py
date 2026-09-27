from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.tasks.schemas import (
    TaskCreateRequest,
    TaskResponse,
)
from app.tasks.service import task_service

router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["EVU Background Tasks"],
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_task(
    request: TaskCreateRequest,
    current_user=Depends(get_current_user),
):
    return await task_service.create(
        request
    )


@router.get(
    "",
    response_model=list[TaskResponse],
)
async def list_tasks(
    current_user=Depends(get_current_user),
):
    return task_service.list()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
async def get_task(
    task_id: str,
    current_user=Depends(get_current_user),
):
    task = task_service.get(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    return task


@router.delete(
    "/{task_id}",
)
async def cancel_task(
    task_id: str,
    current_user=Depends(get_current_user),
):
    cancelled = task_service.cancel(
        task_id
    )

    if not cancelled:
        raise HTTPException(
            status_code=400,
            detail=(
                "Task cannot be cancelled "
                "or has already completed."
            ),
        )

    return {
        "task_id": task_id,
        "status": "cancelled",
    }