import os
import re
from pathlib import Path
from typing import Optional
from app.skills.models import SkillDefinition


class SkillLoader:
    """Parses standard SKILL.md documentation into SkillDefinition objects."""

    @staticmethod
    def load_from_markdown(file_path: str | Path) -> Optional[SkillDefinition]:
        path = Path(file_path)
        if not path.exists():
            return None

        content = path.read_text(encoding="utf-8")

        # Parse YAML frontmatter if available
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if frontmatter_match:
            raw_meta, instructions = frontmatter_match.groups()
            meta_dict = {}
            for line in raw_meta.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta_dict[key.strip()] = val.strip()

            tags = [t.strip() for t in meta_dict.get("tags", "").split(",") if t.strip()]
            tools = [t.strip() for t in meta_dict.get("required_tools", "").split(",") if t.strip()]

            return SkillDefinition(
                name=meta_dict.get("name", path.stem),
                description=meta_dict.get("description", ""),
                domain=meta_dict.get("domain", "general"),
                version=meta_dict.get("version"),
                instructions=instructions.strip(),
                tags=tags,
                required_tools=tools,
                safety_level=meta_dict.get("safety_level", "standard"),
            )

        # Fallback to plain markdown
        return SkillDefinition(
            name=path.stem,
            description="Loaded from markdown specification",
            domain="general",
            instructions=content.strip(),
        )

    @classmethod
    def load_directory(cls, dir_path: str | Path) -> list[SkillDefinition]:
        root = Path(dir_path)
        skills = []
        for md_file in root.glob("**/*.md"):
            skill = cls.load_from_markdown(md_file)
            if skill:
                skills.append(skill)
        return skills