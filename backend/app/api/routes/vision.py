from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.multimodal.schemas import (
    VisionRequest,
    VisionResponse,
)
from app.multimodal.service import (
    multimodal_service,
)


router = APIRouter(
    prefix="/api/v1/vision",
    tags=["EVU Vision Intelligence"],
)


@router.post(
    "/analyze",
    response_model=VisionResponse,
)
async def analyze_image(
    request: VisionRequest,
    current_user=Depends(get_current_user),
):
    return await multimodal_service.analyze_image(
        asset_id=request.asset_id,
        prompt=request.prompt,
    )