from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class SkillDescriptor:
    name: str
    description: str = ""

    version: str = "1.0.0"

    capabilities: List[str] = field(
        default_factory=list
    )

    tools: List[str] = field(
        default_factory=list
    )

    tags: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    enabled: bool = True


class SkillDiscovery:
    def __init__(self) -> None:
        self._skills: Dict[str, SkillDescriptor] = {}

    def register(
        self,
        skill: SkillDescriptor,
    ) -> SkillDescriptor:
        self._skills[skill.name] = skill
        return skill

    def unregister(
        self,
        name: str,
    ) -> bool:
        return (
            self._skills.pop(name, None)
            is not None
        )

    def get(
        self,
        name: str,
    ) -> Optional[SkillDescriptor]:
        return self._skills.get(name)

    def find_by_capability(
        self,
        capability: str,
    ) -> List[SkillDescriptor]:
        return [
            skill
            for skill in self._skills.values()
            if skill.enabled
            and capability in skill.capabilities
        ]

    def find_by_tag(
        self,
        tag: str,
    ) -> List[SkillDescriptor]:
        return [
            skill
            for skill in self._skills.values()
            if skill.enabled
            and tag in skill.tags
        ]

    def search(
        self,
        query: str,
    ) -> List[SkillDescriptor]:
        query = query.lower().strip()

        if not query:
            return []

        results: list[SkillDescriptor] = []

        for skill in self._skills.values():
            searchable = " ".join(
                [
                    skill.name,
                    skill.description,
                    *skill.capabilities,
                    *skill.tags,
                ]
            ).lower()

            if query in searchable:
                results.append(skill)

        return results

    def list(
        self,
        enabled_only: bool = True,
    ) -> List[SkillDescriptor]:
        skills = list(self._skills.values())

        if enabled_only:
            skills = [
                skill
                for skill in skills
                if skill.enabled
            ]

        return skills