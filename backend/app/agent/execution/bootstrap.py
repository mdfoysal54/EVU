from app.agent.execution.registry import tool_registry


async def calculator_handler(arguments: dict):
    from app.agent.tools.calculator import calculator_tool
    expression = str(arguments.get("expression", "")).strip()
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
    query = str(arguments.get("query", "")).strip()
    if not query:
        raise ValueError("Missing research query.")
    result = await web_research_tool.run(
        query=query,
        max_results=int(arguments.get("max_results", 5)),
        fetch_pages=int(arguments.get("fetch_pages", 3)),
    )
    if not result.success:
        raise RuntimeError(result.output)
    return result.output


def register_default_tools() -> None:
    definitions = [
        ("calculator", "Safely evaluate a mathematical expression.", calculator_handler),
        ("current_time", "Return the current UTC time.", current_time_handler),
        ("web_research", "Search, fetch, rank and extract public web information.", web_research_handler),
    ]
    for name, description, handler in definitions:
        if tool_registry.get(name) is None:
            tool_registry.register(name=name, description=description, handler=handler)
