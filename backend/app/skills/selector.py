import re
from typing import List
from app.skills.models import SkillDefinition, SkillMetadata
from app.skills.registry import SkillRegistry, skill_registry


class SkillSelector:
    """Progressive disclosure selector: identifies top 2-5 skills from lightweight metadata."""

    def __init__(self, registry: SkillRegistry = skill_registry):
        self.registry = registry

    def score_skill(self, query: str, meta: SkillMetadata) -> float:
        query_words = set(re.findall(r"\w+", query.lower()))
        if not query_words:
            return 0.0

        score = 0.0

        # Exact name match bonus
        if meta.name.lower() in query.lower():
            score += 5.0

        # Tag overlap
        tag_overlap = sum(1 for tag in meta.tags if tag.lower() in query_words)
        score += tag_overlap * 2.0

        # Domain overlap
        if meta.domain.lower() in query_words:
            score += 1.5

        # Description keyword overlap
        desc_words = set(re.findall(r"\w+", meta.description.lower()))
        desc_overlap = len(query_words.intersection(desc_words))
        score += desc_overlap * 0.5

        return score

    def select_candidates(self, query: str, top_k: int = 3) -> List[SkillMetadata]:
        all_meta = self.registry.list_metadata()
        scored = [(meta, self.score_skill(query, meta)) for meta in all_meta]

        # Filter out 0-score items and take the top k
        relevant = [item for item in scored if item[1] > 0.0]
        relevant.sort(key=lambda x: x[1], reverse=True)

        return [item[0] for item in relevant[:top_k]]

    def resolve_instructions(self, query: str, top_k: int = 3) -> List[SkillDefinition]:
        """Progressive hydration: loads full instructions only for selected candidates."""
        candidates = self.select_candidates(query, top_k=top_k)
        resolved = []
        for meta in candidates:
            full_skill = self.registry.get(meta.name)
            if full_skill:
                resolved.append(full_skill)
        return resolved