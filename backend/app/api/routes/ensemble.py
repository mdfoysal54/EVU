from fastapi import APIRouter, Depends, HTTPException

from app.ai.ensemble.engine import evu_ensemble
from app.ai.ensemble.schemas import EnsembleRequest, EnsembleResponse
from app.api.dependencies import get_current_user
from app.database.models import User


router = APIRouter(
    prefix="/api/v1/ensemble",
    tags=["EVU Ensemble"],
)


@router.post("/run", response_model=EnsembleResponse)
async def run_ensemble(
    request: EnsembleRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        return await evu_ensemble.run(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"EVU ensemble error: {exc}") from exc