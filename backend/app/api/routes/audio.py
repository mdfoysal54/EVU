from fastapi import APIRouter, Depends
from app.core.security import get_current_user

from app.auth.dependencies import get_current_user
from app.multimodal.schemas import (
    AudioTranscriptionRequest,
    AudioTranscriptionResponse,
)
from app.multimodal.service import (
    multimodal_service,
)


router = APIRouter(
    prefix="/api/v1/audio",
    tags=["EVU Audio Intelligence"],
)


@router.post(
    "/transcribe",
    response_model=AudioTranscriptionResponse,
)
async def transcribe_audio(
    request: AudioTranscriptionRequest,
    current_user=Depends(
        get_current_user
    ),
):

    return await (
        multimodal_service.transcribe_audio(
            asset_id=request.asset_id,
            language=request.language,
            prompt=request.prompt,
        )
    )