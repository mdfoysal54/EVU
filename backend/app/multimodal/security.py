from pathlib import Path

from app.core.config import settings


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/ogg",
    "audio/webm",
    "audio/mp4",
    "audio/x-m4a",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-matroska",
}

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/json",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def get_modality(media_type: str) -> str | None:
    media_type = media_type.lower().strip()

    if media_type in ALLOWED_IMAGE_TYPES:
        return "image"

    if media_type in ALLOWED_AUDIO_TYPES:
        return "audio"

    if media_type in ALLOWED_VIDEO_TYPES:
        return "video"

    if media_type in ALLOWED_DOCUMENT_TYPES:
        return "document"

    return None


def is_allowed_media_type(media_type: str) -> bool:
    return get_modality(media_type) is not None


def get_max_size_bytes(modality: str) -> int:
    if modality == "image":
        return settings.MULTIMODAL_MAX_IMAGE_SIZE_MB * 1024 * 1024

    if modality == "audio":
        return settings.MULTIMODAL_MAX_AUDIO_SIZE_MB * 1024 * 1024

    if modality == "video":
        return settings.MULTIMODAL_MAX_VIDEO_SIZE_MB * 1024 * 1024

    if modality == "document":
        return settings.MULTIMODAL_MAX_DOCUMENT_SIZE_MB * 1024 * 1024

    return settings.MULTIMODAL_MAX_FILE_SIZE_MB * 1024 * 1024


def safe_filename(filename: str) -> str:
    """
    Prevent path traversal and normalize the filename.
    """

    name = Path(filename or "upload").name

    name = name.replace("\x00", "")
    name = name.strip()

    if not name:
        return "upload"

    return name[:255]