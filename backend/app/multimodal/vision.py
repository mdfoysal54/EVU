import base64
from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import settings
from app.multimodal.schemas import VisionResponse


class VisionService:

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

    @staticmethod
    def _mime_to_data_url(
        media_type: str,
        file_bytes: bytes,
    ) -> str:

        encoded = base64.b64encode(
            file_bytes
        ).decode("utf-8")

        return (
            f"data:{media_type};base64,{encoded}"
        )

    async def analyze(
        self,
        asset_id: str,
        file_path: Path,
        media_type: str,
        prompt: str,
    ) -> VisionResponse:

        try:

            if not file_path.exists():

                return VisionResponse(
                    asset_id=asset_id,
                    model=settings.VISION_MODEL,
                    prompt=prompt,
                    answer="",
                    success=False,
                    error="Image file was not found.",
                )

            file_bytes = file_path.read_bytes()

            if not file_bytes:

                return VisionResponse(
                    asset_id=asset_id,
                    model=settings.VISION_MODEL,
                    prompt=prompt,
                    answer="",
                    success=False,
                    error="Image file is empty.",
                )

            data_url = self._mime_to_data_url(
                media_type=media_type,
                file_bytes=file_bytes,
            )

            client = self._get_client()

            response = await client.responses.create(
                model=settings.VISION_MODEL,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": prompt,
                            },
                            {
                                "type": "input_image",
                                "image_url": data_url,
                            },
                        ],
                    }
                ],
            )

            answer = (
                getattr(
                    response,
                    "output_text",
                    None,
                )
                or ""
            ).strip()

            if not answer:

                answer = (
                    "The vision model returned "
                    "no textual answer."
                )

            return VisionResponse(
                asset_id=asset_id,
                model=settings.VISION_MODEL,
                prompt=prompt,
                answer=answer,
                success=True,
            )

        except Exception as exc:

            return VisionResponse(
                asset_id=asset_id,
                model=settings.VISION_MODEL,
                prompt=prompt,
                answer="",
                success=False,
                error=str(exc),
            )


vision_service = VisionService()