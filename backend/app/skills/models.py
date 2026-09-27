from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SkillMetadata:
    """Lightweight metadata descriptor used for zero-cost prompt routing."""
    name: str
    description: str
    domain: str
    tags: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    safety_level: str = "standard"
    enabled: bool = True


@dataclass
class SkillDefinition:
    """Universal internal representation of a fully hydrated EVU skill."""
    name: str
    description: str
    domain: str
    version: Optional[str] = None
    instructions: str = ""
    tags: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    required_packages: List[str] = field(default_factory=list)
    required_env: List[str] = field(default_factory=list)
    safety_level: str = "standard"
    source: str = "evu"
    enabled: bool = True

    def to_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name=self.name,
            description=self.description,
            domain=self.domain,
            tags=self.tags,
            required_tools=self.required_tools,
            safety_level=self.safety_level,
            enabled=self.enabled,
        )