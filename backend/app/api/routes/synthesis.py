from fastapi import APIRouter, Depends, HTTPException

from app.ai.synthesis.engine import synthesis_engine
from app.ai.synthesis.schemas import (
    SynthesisRequest,
    SynthesisResponse,
)
from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/synthesis",
    tags=["EVU Multi-Model Synthesis"],
)


@router.post(
    "",
    response_model=SynthesisResponse,
)
async def synthesize(
    request: SynthesisRequest,
    current_user=Depends(get_current_user),
):
    """
    Combine multiple model responses into one final answer.
    """

    try:
        return await synthesis_engine.run(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Synthesis failed: {exc}",
        ) from exc