from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import settings
from app.multimodal.schemas import (
    AudioTranscriptionResponse,
)


class AudioService:

    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:

        if self._client is None:

            if not settings.OPENAI_API_KEY:
                raise RuntimeError(
                    "OPENAI_API_KEY is not configured."
                )

            self._client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY
            )

        return self._client

    async def transcribe(
        self,
        asset_id: str,
        file_path: Path,
        language: str | None = None,
        prompt: str | None = None,
    ) -> AudioTranscriptionResponse:

        try:

            if not file_path.exists():

                return AudioTranscriptionResponse(
                    asset_id=asset_id,
                    model=settings.AUDIO_TRANSCRIPTION_MODEL,
                    transcript="",
                    language=language,
                    success=False,
                    error="Audio file was not found.",
                )

            if file_path.stat().st_size == 0:

                return AudioTranscriptionResponse(
                    asset_id=asset_id,
                    model=settings.AUDIO_TRANSCRIPTION_MODEL,
                    transcript="",
                    language=language,
                    success=False,
                    error="Audio file is empty.",
                )

            client = self._get_client()

            with file_path.open("rb") as audio_file:

                request_kwargs = {
                    "model": settings.AUDIO_TRANSCRIPTION_MODEL,
                    "file": audio_file,
                }

                if language:
                    request_kwargs["language"] = language

                if prompt:
                    request_kwargs["prompt"] = prompt

                response = (
                    await client.audio.transcriptions.create(
                        **request_kwargs
                    )
                )

            transcript = (
                getattr(
                    response,
                    "text",
                    None,
                )
                or ""
            ).strip()

            return AudioTranscriptionResponse(
                asset_id=asset_id,
                model=settings.AUDIO_TRANSCRIPTION_MODEL,
                transcript=transcript,
                language=language,
                success=True,
            )

        except Exception as exc:

            return AudioTranscriptionResponse(
                asset_id=asset_id,
                model=settings.AUDIO_TRANSCRIPTION_MODEL,
                transcript="",
                language=language,
                success=False,
                error=str(exc),
            )


audio_service = AudioService()