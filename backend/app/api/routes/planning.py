from fastapi import APIRouter, Depends, HTTPException

from app.agent.planning.engine import planning_engine
from app.agent.planning.schemas import (
    PlanningRequest,
    PlanningResponse,
)
from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/planning",
    tags=["EVU Agent Planning"],
)


@router.post(
    "",
    response_model=PlanningResponse,
)
async def create_plan(
    request: PlanningRequest,
    current_user=Depends(get_current_user),
):
    """
    Create an execution plan for a complex request.
    """

    try:
        return await planning_engine.run(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Planning failed: {exc}",
        ) from exc