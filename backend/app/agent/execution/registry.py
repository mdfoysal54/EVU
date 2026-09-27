from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


ToolCallable = Callable[
    [dict[str, Any]],
    Awaitable[Any],
]


@dataclass
class RegisteredTool:
    name: str
    description: str
    handler: ToolCallable
    enabled: bool = True


class ToolRegistry:

    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(
        self,
        name: str,
        description: str,
        handler: ToolCallable,
        enabled: bool = True,
    ) -> None:

        self._tools[name] = RegisteredTool(
            name=name,
            description=description,
            handler=handler,
            enabled=enabled,
        )

    def get(
        self,
        name: str,
    ) -> RegisteredTool | None:

        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:

        return [
            {
                "name": tool.name,
                "description": tool.description,
                "enabled": tool.enabled,
            }
            for tool in self._tools.values()
        ]

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:

        tool = self.get(name)

        if tool is None:
            raise ValueError(
                f"Tool '{name}' is not registered."
            )

        if not tool.enabled:
            raise ValueError(
                f"Tool '{name}' is disabled."
            )

        return await tool.handler(arguments)


tool_registry = ToolRegistry()