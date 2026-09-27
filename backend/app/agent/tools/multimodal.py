from app.agent.tools.base import ToolExecution
from app.multimodal.service import multimodal_service


class MultimodalTool:
    name = "multimodal"

    description = (
        "Manages EVU multimodal assets such as images, audio, "
        "video and documents. It can inspect asset metadata, "
        "create multimodal input references, and delete assets."
    )

    async def run(
        self,
        action: str,
        asset_id: str = "",
        text: str = "",
        asset_ids: list[str] | None = None,
    ) -> ToolExecution:

        try:
            if action == "inspect":

                if not asset_id:
                    return ToolExecution(
                        success=False,
                        output="",
                        error="asset_id is required.",
                    )

                asset = multimodal_service.get_asset(
                    asset_id
                )

                if asset is None:
                    return ToolExecution(
                        success=False,
                        output="",
                        error="Asset not found.",
                    )

                return ToolExecution(
                    success=True,
                    output=asset.model_dump_json(),
                    error=None,
                )

            if action == "request":

                references = asset_ids or []

                response = multimodal_service.build_request(
                    text=text or None,
                    asset_ids=references,
                )

                return ToolExecution(
                    success=response.success,
                    output=response.model_dump_json(),
                    error=response.error,
                )

            if action == "delete":

                if not asset_id:
                    return ToolExecution(
                        success=False,
                        output="",
                        error="asset_id is required.",
                    )

                response = multimodal_service.delete(
                    asset_id
                )

                return ToolExecution(
                    success=response.success,
                    output=response.model_dump_json(),
                    error=response.error,
                )

            return ToolExecution(
                success=False,
                output="",
                error=(
                    "Unsupported action. "
                    "Use inspect, request, or delete."
                ),
            )

        except Exception as exc:
            return ToolExecution(
                success=False,
                output="",
                error=str(exc),
            )


multimodal_tool = MultimodalTool()