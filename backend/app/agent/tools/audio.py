from app.agent.tools.base import ToolExecution
from app.multimodal.service import (
    multimodal_service,
)


class AudioTool:

    name = "audio"

    description = (
        "Transcribes an audio asset into text "
        "using EVU audio intelligence."
    )

    async def run(
        self,
        asset_id: str,
        language: str = "",
        prompt: str = "",
    ) -> ToolExecution:

        if not asset_id:

            return ToolExecution(
                success=False,
                output="",
                error=(
                    "asset_id is required."
                ),
            )

        result = (
            await multimodal_service.transcribe_audio(
                asset_id=asset_id,
                language=language or None,
                prompt=prompt or None,
            )
        )

        return ToolExecution(
            success=result.success,
            output=result.model_dump_json(),
            error=result.error,
        )


audio_tool = AudioTool()