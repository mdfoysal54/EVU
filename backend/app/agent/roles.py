from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    CODER = "coder"
    ANALYST = "analyst"
    WRITER = "writer"
    REVIEWER = "reviewer"
    PLANNER = "planner"
    VERIFIER = "verifier"
    TOOL_OPERATOR = "tool_operator"
    GENERAL = "general"


@dataclass
class RoleDefinition:
    role: AgentRole
    description: str
    responsibilities: List[str] = field(
        default_factory=list
    )
    preferred_capabilities: List[str] = field(
        default_factory=list
    )
    allowed_tools: List[str] = field(
        default_factory=list
    )
    system_prompt: str = ""


class RoleRegistry:
    def __init__(self) -> None:
        self._roles: Dict[str, RoleDefinition] = {}

        self._register_defaults()

    def register(
        self,
        definition: RoleDefinition,
    ) -> None:
        self._roles[definition.role.value] = definition

    def get(
        self,
        role: str | AgentRole,
    ) -> Optional[RoleDefinition]:
        key = (
            role.value
            if isinstance(role, AgentRole)
            else role
        )

        return self._roles.get(key)

    def list(self) -> List[RoleDefinition]:
        return list(self._roles.values())

    def _register_defaults(self) -> None:
        self.register(
            RoleDefinition(
                role=AgentRole.ORCHESTRATOR,
                description="Coordinates multiple agents and tasks.",
                responsibilities=[
                    "Decompose tasks",
                    "Delegate work",
                    "Aggregate results",
                    "Coordinate verification",
                ],
                preferred_capabilities=[
                    "planning",
                    "delegation",
                    "reasoning",
                ],
            )
        )

        self.register(
            RoleDefinition(
                role=AgentRole.RESEARCHER,
                description="Collects and analyzes information.",
                responsibilities=[
                    "Search sources",
                    "Extract evidence",
                    "Track citations",
                    "Summarize findings",
                ],
                preferred_capabilities=[
                    "research",
                    "web_search",
                    "source_analysis",
                ],
            )
        )

        self.register(
            RoleDefinition(
                role=AgentRole.CODER,
                description="Designs and implements software.",
                responsibilities=[
                    "Write code",
                    "Debug code",
                    "Review architecture",
                    "Run tests",
                ],
                preferred_capabilities=[
                    "coding",
                    "debugging",
                    "software_architecture",
                ],
            )
        )

        self.register(
            RoleDefinition(
                role=AgentRole.ANALYST,
                description="Analyzes structured and unstructured information.",
                responsibilities=[
                    "Analyze data",
                    "Compare alternatives",
                    "Identify patterns",
                ],
                preferred_capabilities=[
                    "analysis",
                    "reasoning",
                    "data_analysis",
                ],
            )
        )

        self.register(
            RoleDefinition(
                role=AgentRole.REVIEWER,
                description="Reviews outputs for correctness and quality.",
                responsibilities=[
                    "Check results",
                    "Find errors",
                    "Provide feedback",
                ],
                preferred_capabilities=[
                    "verification",
                    "review",
                    "reasoning",
                ],
            )
        )

        self.register(
            RoleDefinition(
                role=AgentRole.WRITER,
                description="Produces structured written content.",
                responsibilities=[
                    "Draft content",
                    "Edit content",
                    "Improve clarity",
                ],
                preferred_capabilities=[
                    "writing",
                    "editing",
                ],
            )
        )

        self.register(
            RoleDefinition(
                role=AgentRole.VERIFIER,
                description="Validates outputs against requirements.",
                responsibilities=[
                    "Validate assertions",
                    "Run checks",
                    "Detect regressions",
                ],
                preferred_capabilities=[
                    "verification",
                    "testing",
                    "reasoning",
                ],
            )
        )

        self.register(
            RoleDefinition(
                role=AgentRole.GENERAL,
                description="General-purpose EVU agent.",
            )
        )