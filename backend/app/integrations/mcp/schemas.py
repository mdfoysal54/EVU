from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MCPServerConfig:
    name: str
    command: str | None = None
    args: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)
    url: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0
    enabled: bool = True


@dataclass(frozen=True)
class MCPTool:
    name: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    server: str | None = None


@dataclass(frozen=True)
class MCPResource:
    uri: str
    name: str = ""
    description: str = ""
    mime_type: str | None = None
    server: str | None = None


@dataclass(frozen=True)
class MCPPrompt:
    name: str
    description: str = ""
    arguments: tuple[dict[str, Any], ...] = ()
    server: str | None = None


@dataclass(frozen=True)
class MCPResponse:
    result: Any = None
    error: dict[str, Any] | None = None
    request_id: str | int | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def raise_for_error(self) -> Any:
        if self.error is not None:
            raise RuntimeError(str(self.error))
        return self.result
