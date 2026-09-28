from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid


@dataclass
class AgentCapability:
    name: str
    description: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.confidence = max(
            0.0,
            min(1.0, float(self.confidence)),
        )


@dataclass
class AgentProfile:
    name: str
    agent_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    description: str = ""

    system_prompt: str = ""

    model: Optional[str] = None
    provider: Optional[str] = None

    role: Optional[str] = None

    capabilities: List[AgentCapability] = field(
        default_factory=list
    )

    tools: List[str] = field(default_factory=list)

    tags: List[str] = field(default_factory=list)

    temperature: float = 0.2
    max_tokens: Optional[int] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    enabled: bool = True

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def add_capability(
        self,
        capability: AgentCapability,
    ) -> None:
        existing = next(
            (
                item
                for item in self.capabilities
                if item.name == capability.name
            ),
            None,
        )

        if existing is not None:
            self.capabilities.remove(existing)

        self.capabilities.append(capability)
        self.touch()

    def has_capability(
        self,
        capability_name: str,
    ) -> bool:
        return any(
            capability.name == capability_name
            for capability in self.capabilities
        )

    def capability_score(
        self,
        capability_name: str,
    ) -> float:
        for capability in self.capabilities:
            if capability.name == capability_name:
                return capability.confidence

        return 0.0

    def add_tool(self, tool_name: str) -> None:
        if tool_name not in self.tools:
            self.tools.append(tool_name)

        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)