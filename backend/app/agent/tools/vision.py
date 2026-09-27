from app.agent.tools.base import ToolExecution
from app.multimodal.service import (
    multimodal_service,
)


class VisionTool:

    name = "vision"

    description = (
        "Analyzes an image asset using EVU's "
        "vision intelligence system."
    )

    async def run(
        self,
        asset_id: str,
        prompt: str = (
            "Describe this image in detail."
        ),
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
            await multimodal_service.analyze_image(
                asset_id=asset_id,
                prompt=prompt,
            )
        )

        return ToolExecution(
            success=result.success,
            output=result.model_dump_json(),
            error=result.error,
        )


vision_tool = VisionTool()