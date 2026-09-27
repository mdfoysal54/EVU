from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

MultimodalType = Literal[
    "image",
    "audio",
    "video",
    "document",
    "text",
]


class MultimodalAssetResponse(BaseModel):
    asset_id: str
    original_filename: str
    stored_filename: str
    media_type: str
    modality: MultimodalType
    size_bytes: int
    sha256: str
    width: int | None = None
    height: int | None = None
    duration_seconds: float | None = None
    created_at: datetime
    success: bool = True
    error: str | None = None


class MultimodalInput(BaseModel):
    asset_id: str
    modality: MultimodalType
    media_type: str
    original_filename: str
    size_bytes: int
    sha256: str


class MultimodalRequest(BaseModel):
    text: str | None = None
    asset_ids: list[str] = Field(default_factory=list)


class MultimodalResponse(BaseModel):
    request_id: str
    text: str | None = None
    assets: list[MultimodalAssetResponse] = Field(default_factory=list)
    success: bool = True
    error: str | None = None


class MultimodalDeleteResponse(BaseModel):
    asset_id: str
    deleted: bool
    success: bool = True
    error: str | None = None


# =========================================================
# VISION
# =========================================================


class VisionRequest(BaseModel):
    asset_id: str
    prompt: str = (
        "Describe this image in detail. "
        "Identify important objects, visible text, "
        "people, environment, and other relevant details."
    )


class VisionResponse(BaseModel):
    asset_id: str
    model: str
    prompt: str
    answer: str
    success: bool = True
    error: str | None = None


# =========================================================
# AUDIO
# =========================================================


class AudioTranscriptionRequest(BaseModel):
    asset_id: str
    language: str | None = None
    prompt: str | None = None


class AudioTranscriptionResponse(BaseModel):
    asset_id: str
    model: str
    transcript: str
    language: str | None = None
    duration_seconds: float | None = None
    success: bool = True
    error: str | None = None


# =========================================================
# MULTIMODAL ANALYSIS
# =========================================================


class MultimodalAnalysisRequest(BaseModel):
    text: str | None = None
    image_asset_ids: list[str] = Field(default_factory=list)
    audio_asset_ids: list[str] = Field(default_factory=list)


class MultimodalAnalysisResponse(BaseModel):
    request_id: str
    answer: str
    transcripts: list[AudioTranscriptionResponse] = Field(default_factory=list)
    vision_results: list[VisionResponse] = Field(default_factory=list)
    success: bool = True
    error: str | None = None