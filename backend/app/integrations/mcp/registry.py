from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .client import MCPClient
from .schemas import MCPServerConfig, MCPTool


@dataclass(frozen=True)
class RegisteredTool:
    server: str
    tool: MCPTool


class MCPRegistry:
    def __init__(self) -> None:
        self._configs: dict[str, MCPServerConfig] = {}
        self._clients: dict[str, MCPClient] = {}

    def register(self, config: MCPServerConfig) -> MCPClient:
        client = MCPClient(config)
        self._configs[config.name] = config
        self._clients[config.name] = client
        return client

    def unregister(self, name: str) -> bool:
        client = self._clients.pop(name, None)
        self._configs.pop(name, None)
        if client is None:
            return False
        client.close()
        return True

    def get(self, name: str) -> MCPClient:
        try:
            return self._clients[name]
        except KeyError as exc:
            raise KeyError(f"Unknown MCP server: {name}") from exc

    def servers(self) -> list[str]:
        return list(self._clients)

    def discover_tools(self) -> list[RegisteredTool]:
        tools: list[RegisteredTool] = []
        for name, client in self._clients.items():
            if not self._configs[name].enabled:
                continue
            for tool in client.list_tools():
                tools.append(RegisteredTool(name, tool))
        return tools

    def call_tool(self, server: str, tool: str, arguments: dict[str, Any] | None = None) -> Any:
        return self.get(server).call_tool(tool, arguments)

    def close(self) -> None:
        for client in self._clients.values():
            client.close()


mcp_registry = MCPRegistry()
