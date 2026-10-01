from datetime import datetime, timezone
from app.agent.tools.base import ToolExecution


class CurrentTimeTool:
    name = "current_time"

    def run(self, _: str = "") -> ToolExecution:
        now = datetime.now(timezone.utc)
        return ToolExecution(name=self.name, input="UTC", output=now.isoformat())


current_time_tool = CurrentTimeTool()


async def get_current_time() -> str:
    """Legacy async compatibility helper used by the execution tool registry."""
    return current_time_tool.run().output
