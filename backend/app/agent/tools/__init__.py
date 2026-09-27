from app.agent.tools.audio import audio_tool
from app.agent.tools.browser import browser_tool
from app.agent.tools.calculator import calculator_tool
from app.agent.tools.current_time import current_time_tool
from app.agent.tools.diagram_tool import diagram_tool
from app.agent.tools.document_search import document_search_tool
from app.agent.tools.multimodal import multimodal_tool
from app.agent.tools.vision import vision_tool
from app.agent.tools.web_research import web_research_tool


async def _calc_exec_handler(arguments: dict):
    from app.agent.tools.calculator import calculator_tool as existing

    expression = arguments.get("expression")
    if not expression:
        raise ValueError("Missing 'expression' argument.")

    return await existing(expression)


async def _time_exec_handler(arguments: dict):
    from app.agent.tools.current_time import get_current_time

    return await get_current_time()


async def _diagram_exec_handler(arguments: dict):
    from app.agent.tools.diagram_tool import diagram_tool as existing

    diagram_ir_payload = arguments.get("diagram_ir_payload", arguments)
    return existing(diagram_ir_payload)


def register_execution_tools() -> None:
    # Deferred import prevents circular import deadlock on startup
    from app.agent.execution.registry import tool_registry

    tool_registry.register(
        name="calculator",
        description="Safely evaluate a mathematical expression.",
        handler=_calc_exec_handler,
    )

    tool_registry.register(
        name="current_time",
        description="Get the current UTC time.",
        handler=_time_exec_handler,
    )

    tool_registry.register(
        name="diagram",
        description="Validate and render a structured DiagramIR payload into an accessible SVG diagram.",
        handler=_diagram_exec_handler,
    )


__all__ = [
    "audio_tool",
    "browser_tool",
    "calculator_tool",
    "current_time_tool",
    "diagram_tool",
    "document_search_tool",
    "multimodal_tool",
    "vision_tool",
    "web_research_tool",
    "register_execution_tools",
]