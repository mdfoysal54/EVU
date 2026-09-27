from fastapi import APIRouter, Depends, HTTPException

from app.ai.evaluation.engine import evu_evaluation_engine
from app.ai.evaluation.schemas import JudgeRequest, JudgeResponse
from app.api.dependencies import get_current_user
from app.database.models import User


router = APIRouter(
    prefix="/api/v1/evaluation",
    tags=["EVU Evaluation"],
)


@router.post("/judge", response_model=JudgeResponse)
async def judge_answers(
    request: JudgeRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        return await evu_evaluation_engine.run(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"EVU evaluation error: {exc}",
        ) from exc