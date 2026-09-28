from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json


@dataclass
class AgentSkill:
    """
    EVU internal representation of an Agent Skill.

    The format is deliberately provider-neutral so skills can later
    be loaded from Markdown/YAML/JSON or external skill packages.
    """

    name: str

    description: str

    instructions: str

    version: str = "1.0.0"

    capabilities: List[str] = field(
        default_factory=list
    )

    tools: List[str] = field(
        default_factory=list
    )

    inputs: Dict[str, Any] = field(
        default_factory=dict
    )

    outputs: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "instructions": self.instructions,
            "version": self.version,
            "capabilities": list(self.capabilities),
            "tools": list(self.tools),
            "inputs": dict(self.inputs),
            "outputs": dict(self.outputs),
            "metadata": dict(self.metadata),
            "enabled": self.enabled,
        }

    def to_json(
        self,
        indent: int = 2,
    ) -> str:
        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
        )

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "AgentSkill":
        required = [
            "name",
            "description",
            "instructions",
        ]

        missing = [
            key
            for key in required
            if key not in data
        ]

        if missing:
            raise ValueError(
                "Missing required skill fields: "
                + ", ".join(missing)
            )

        return cls(
            name=str(data["name"]),
            description=str(data["description"]),
            instructions=str(data["instructions"]),
            version=str(
                data.get("version", "1.0.0")
            ),
            capabilities=list(
                data.get("capabilities", [])
            ),
            tools=list(
                data.get("tools", [])
            ),
            inputs=dict(
                data.get("inputs", {})
            ),
            outputs=dict(
                data.get("outputs", {})
            ),
            metadata=dict(
                data.get("metadata", {})
            ),
            enabled=bool(
                data.get("enabled", True)
            ),
        )

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "AgentSkill":
        data = json.loads(value)

        if not isinstance(data, dict):
            raise ValueError(
                "Skill JSON must contain an object."
            )

        return cls.from_dict(data)

    def validate(self) -> List[str]:
        errors: list[str] = []

        if not self.name.strip():
            errors.append(
                "Skill name cannot be empty."
            )

        if not self.description.strip():
            errors.append(
                "Skill description cannot be empty."
            )

        if not self.instructions.strip():
            errors.append(
                "Skill instructions cannot be empty."
            )

        if not self.version.strip():
            errors.append(
                "Skill version cannot be empty."
            )

        return errors