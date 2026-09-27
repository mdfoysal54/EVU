from datetime import datetime, timezone
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.multimodal.audio import audio_service
from app.multimodal.schemas import (
    AudioTranscriptionResponse,
    MultimodalAssetResponse,
    MultimodalDeleteResponse,
    MultimodalInput,
    MultimodalResponse,
    VisionResponse,
)
from app.multimodal.security import (
    get_max_size_bytes,
    get_modality,
    is_allowed_media_type,
    safe_filename,
)
from app.multimodal.storage import multimodal_storage
from app.multimodal.vision import vision_service


class MultimodalService:

    def __init__(self) -> None:

        self.metadata: dict[
            str,
            MultimodalAssetResponse,
        ] = {}

    # =====================================================
    # UPLOAD
    # =====================================================

    async def upload(
        self,
        upload: UploadFile,
    ) -> MultimodalAssetResponse:

        if not settings.MULTIMODAL_ENABLED:

            return MultimodalAssetResponse(
                asset_id="",
                original_filename=(
                    upload.filename or "upload"
                ),
                stored_filename="",
                media_type=(
                    upload.content_type or ""
                ),
                modality="document",
                size_bytes=0,
                sha256="",
                created_at=datetime.now(
                    timezone.utc
                ),
                success=False,
                error=(
                    "Multimodal input is disabled."
                ),
            )

        media_type = (
            upload.content_type
            or "application/octet-stream"
        ).lower()

        if not is_allowed_media_type(
            media_type
        ):

            return MultimodalAssetResponse(
                asset_id="",
                original_filename=(
                    upload.filename or "upload"
                ),
                stored_filename="",
                media_type=media_type,
                modality="document",
                size_bytes=0,
                sha256="",
                created_at=datetime.now(
                    timezone.utc
                ),
                success=False,
                error=(
                    f"Unsupported media type: "
                    f"{media_type}"
                ),
            )

        modality = get_modality(
            media_type
        )

        if modality is None:

            return MultimodalAssetResponse(
                asset_id="",
                original_filename=(
                    upload.filename or "upload"
                ),
                stored_filename="",
                media_type=media_type,
                modality="document",
                size_bytes=0,
                sha256="",
                created_at=datetime.now(
                    timezone.utc
                ),
                success=False,
                error=(
                    "Could not determine input "
                    "modality."
                ),
            )

        filename = safe_filename(
            upload.filename or "upload"
        )

        asset_id = (
            multimodal_storage.create_asset_id()
        )

        max_size = get_max_size_bytes(
            modality
        )

        try:

            (
                stored_path,
                size_bytes,
                sha256,
            ) = await multimodal_storage.save_upload(
                upload=upload,
                asset_id=asset_id,
                max_size_bytes=max_size,
            )

        except ValueError as exc:

            return MultimodalAssetResponse(
                asset_id=asset_id,
                original_filename=filename,
                stored_filename="",
                media_type=media_type,
                modality=modality,
                size_bytes=0,
                sha256="",
                created_at=datetime.now(
                    timezone.utc
                ),
                success=False,
                error=str(exc),
            )

        except Exception as exc:

            return MultimodalAssetResponse(
                asset_id=asset_id,
                original_filename=filename,
                stored_filename="",
                media_type=media_type,
                modality=modality,
                size_bytes=0,
                sha256="",
                created_at=datetime.now(
                    timezone.utc
                ),
                success=False,
                error=(
                    f"Failed to store upload: "
                    f"{exc}"
                ),
            )

        asset = MultimodalAssetResponse(
            asset_id=asset_id,
            original_filename=filename,
            stored_filename=stored_path.name,
            media_type=media_type,
            modality=modality,
            size_bytes=size_bytes,
            sha256=sha256,
            created_at=datetime.now(
                timezone.utc
            ),
            success=True,
        )

        self.metadata[asset_id] = asset

        return asset

    # =====================================================
    # ASSET
    # =====================================================

    def get_asset(
        self,
        asset_id: str,
    ) -> MultimodalAssetResponse | None:

        return self.metadata.get(asset_id)

    def get_input_reference(
        self,
        asset_id: str,
    ) -> MultimodalInput | None:

        asset = self.get_asset(
            asset_id
        )

        if asset is None:
            return None

        return MultimodalInput(
            asset_id=asset.asset_id,
            modality=asset.modality,
            media_type=asset.media_type,
            original_filename=(
                asset.original_filename
            ),
            size_bytes=asset.size_bytes,
            sha256=asset.sha256,
        )

    def get_file_path(
        self,
        asset_id: str,
    ):

        return multimodal_storage.find_asset_file(
            asset_id
        )

    # =====================================================
    # VISION
    # =====================================================

    async def analyze_image(
        self,
        asset_id: str,
        prompt: str,
    ) -> VisionResponse:

        asset = self.get_asset(
            asset_id
        )

        if asset is None:

            return VisionResponse(
                asset_id=asset_id,
                model=settings.VISION_MODEL,
                prompt=prompt,
                answer="",
                success=False,
                error="Asset not found.",
            )

        if asset.modality != "image":

            return VisionResponse(
                asset_id=asset_id,
                model=settings.VISION_MODEL,
                prompt=prompt,
                answer="",
                success=False,
                error=(
                    "The supplied asset is not "
                    "an image."
                ),
            )

        file_path = self.get_file_path(
            asset_id
        )

        if file_path is None:

            return VisionResponse(
                asset_id=asset_id,
                model=settings.VISION_MODEL,
                prompt=prompt,
                answer="",
                success=False,
                error=(
                    "Image file could not be located."
                ),
            )

        return await vision_service.analyze(
            asset_id=asset_id,
            file_path=file_path,
            media_type=asset.media_type,
            prompt=prompt,
        )

    # =====================================================
    # AUDIO
    # =====================================================

    async def transcribe_audio(
        self,
        asset_id: str,
        language: str | None = None,
        prompt: str | None = None,
    ) -> AudioTranscriptionResponse:

        asset = self.get_asset(
            asset_id
        )

        if asset is None:

            return AudioTranscriptionResponse(
                asset_id=asset_id,
                model=(
                    settings.AUDIO_TRANSCRIPTION_MODEL
                ),
                transcript="",
                language=language,
                success=False,
                error="Asset not found.",
            )

        if asset.modality != "audio":

            return AudioTranscriptionResponse(
                asset_id=asset_id,
                model=(
                    settings.AUDIO_TRANSCRIPTION_MODEL
                ),
                transcript="",
                language=language,
                success=False,
                error=(
                    "The supplied asset is not "
                    "an audio file."
                ),
            )

        file_path = self.get_file_path(
            asset_id
        )

        if file_path is None:

            return AudioTranscriptionResponse(
                asset_id=asset_id,
                model=(
                    settings.AUDIO_TRANSCRIPTION_MODEL
                ),
                transcript="",
                language=language,
                success=False,
                error=(
                    "Audio file could not be located."
                ),
            )

        return await audio_service.transcribe(
            asset_id=asset_id,
            file_path=file_path,
            language=language,
            prompt=prompt,
        )

    # =====================================================
    # GENERIC REQUEST
    # =====================================================

    def build_request(
        self,
        text: str | None,
        asset_ids: list[str],
    ) -> MultimodalResponse:

        request_id = (
            f"mmreq_{uuid4().hex}"
        )

        assets: list[
            MultimodalAssetResponse
        ] = []

        for asset_id in asset_ids:

            asset = self.get_asset(
                asset_id
            )

            if asset is not None:
                assets.append(asset)

        return MultimodalResponse(
            request_id=request_id,
            text=text,
            assets=assets,
            success=True,
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        asset_id: str,
    ) -> MultimodalDeleteResponse:

        if asset_id not in self.metadata:

            return MultimodalDeleteResponse(
                asset_id=asset_id,
                deleted=False,
                success=False,
                error="Asset not found.",
            )

        deleted = (
            multimodal_storage.delete_asset(
                asset_id
            )
        )

        if deleted:
            self.metadata.pop(
                asset_id,
                None,
            )

        return MultimodalDeleteResponse(
            asset_id=asset_id,
            deleted=deleted,
            success=deleted,
            error=(
                None
                if deleted
                else "Failed to delete asset."
            ),
        )


multimodal_service = MultimodalService()