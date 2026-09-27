from dataclasses import dataclass, field


@dataclass
class EVUSkill:
    name: str
    description: str

    instructions: str = ""

    allowed_tools: list[str] = field(
        default_factory=list
    )

    tags: list[str] = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )

    uri: str = ""

    def to_context(self) -> str:
        return (
            f"Skill: {self.name}\n"
            f"Description: {self.description}\n"
            f"Allowed tools: "
            f"{', '.join(self.allowed_tools)}\n\n"
            f"{self.instructions}"
        )