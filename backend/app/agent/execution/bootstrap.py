from app.agent.execution.registry import tool_registry


async def calculator_handler(arguments: dict):
    from app.agent.tools.calculator import calculator_tool

    expression = str(
        arguments.get("expression", "")
    ).strip()

    if not expression:
        raise ValueError("Missing expression.")

    return calculator_tool._evaluate(expression)


async def current_time_handler(arguments: dict):
    from app.agent.tools.current_time import current_time_tool

    result = current_time_tool.run()

    if not result.success:
        raise RuntimeError(result.output)

    return result.output


async def web_research_handler(arguments: dict):
    from app.agent.tools.web_research import web_research_tool

    query = str(
        arguments.get("query", "")
    ).strip()

    if not query:
        raise ValueError("Missing research query.")

    result = await web_research_tool.run(
        query=query,
        max_results=int(
            arguments.get("max_results", 5)
        ),
        fetch_pages=int(
            arguments.get("fetch_pages", 3)
        ),
    )

    if not result.success:
        raise RuntimeError(result.output)

    return result.output


def register_default_tools() -> None:

    if tool_registry.get("calculator") is None:
        tool_registry.register(
            name="calculator",
            description=(
                "Safely evaluate a mathematical expression."
            ),
            handler=calculator_handler,
        )

    if tool_registry.get("current_time") is None:
        tool_registry.register(
            name="current_time",
            description=(
                "Return the current UTC time."
            ),
            handler=current_time_handler,
        )

    if tool_registry.get("web_research") is None:
        tool_registry.register(
            name="web_research",
            description=(
                "Search, fetch, rank and extract information "
                "from public web sources."
            ),
            handler=web_research_handler,
        )