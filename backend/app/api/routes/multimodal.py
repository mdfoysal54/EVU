from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
)

from app.auth.dependencies import (
    get_current_user,
)
from app.multimodal.schemas import (
    MultimodalAssetResponse,
    MultimodalDeleteResponse,
    MultimodalRequest,
    MultimodalResponse,
)
from app.multimodal.service import (
    multimodal_service,
)


router = APIRouter(
    prefix="/api/v1/multimodal",
    tags=["EVU Multimodal Input"],
)


@router.post(
    "/upload",
    response_model=MultimodalAssetResponse,
)
async def upload_multimodal_asset(
    file: UploadFile = File(...),
    current_user=Depends(
        get_current_user
    ),
):

    return await multimodal_service.upload(
        file
    )


@router.get(
    "/assets/{asset_id}",
    response_model=MultimodalAssetResponse,
)
async def get_multimodal_asset(
    asset_id: str,
    current_user=Depends(
        get_current_user
    ),
):

    asset = multimodal_service.get_asset(
        asset_id
    )

    if asset is None:

        return MultimodalAssetResponse(
            asset_id=asset_id,
            original_filename="",
            stored_filename="",
            media_type="",
            modality="document",
            size_bytes=0,
            sha256="",
            created_at=datetime.now(
                timezone.utc
            ),
            success=False,
            error="Asset not found.",
        )

    return asset


@router.post(
    "/request",
    response_model=MultimodalResponse,
)
async def create_multimodal_request(
    request: MultimodalRequest,
    current_user=Depends(
        get_current_user
    ),
):

    return multimodal_service.build_request(
        text=request.text,
        asset_ids=request.asset_ids,
    )


@router.delete(
    "/assets/{asset_id}",
    response_model=MultimodalDeleteResponse,
)
async def delete_multimodal_asset(
    asset_id: str,
    current_user=Depends(
        get_current_user
    ),
):

    return multimodal_service.delete(
        asset_id
    )