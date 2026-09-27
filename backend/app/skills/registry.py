from typing import Dict, List, Optional
from app.skills.models import SkillDefinition, SkillMetadata


class SkillRegistry:
    """In-memory skill catalog enabling fast candidate indexing."""

    def __init__(self):
        self._skills: Dict[str, SkillDefinition] = {}
        self._metadata_cache: Dict[str, SkillMetadata] = {}

    def register(self, skill: SkillDefinition) -> None:
        self._skills[skill.name] = skill
        self._metadata_cache[skill.name] = skill.to_metadata()

    def get(self, name: str) -> Optional[SkillDefinition]:
        return self._skills.get(name)

    def get_metadata(self, name: str) -> Optional[SkillMetadata]:
        return self._metadata_cache.get(name)

    def list_all(self) -> List[SkillDefinition]:
        return [s for s in self._skills.values() if s.enabled]

    def list_metadata(self) -> List[SkillMetadata]:
        return [m for m in self._metadata_cache.values() if m.enabled]

    def find_by_domain(self, domain: str) -> List[SkillMetadata]:
        return [m for m in self.list_metadata() if m.domain.lower() == domain.lower()]


# Global registry instance
skill_registry = SkillRegistry()