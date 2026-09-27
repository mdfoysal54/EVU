import os
from app.skills.models import SkillDefinition


class SkillValidationError(Exception):
    pass


class SkillValidator:
    """Ensures a skill meets EVU security, safety, and dependency standards."""

    @staticmethod
    def validate(skill: SkillDefinition) -> bool:
        if not skill.name or not skill.name.strip():
            raise SkillValidationError("Skill must possess a non-empty name.")

        if not skill.domain:
            raise SkillValidationError(f"Skill '{skill.name}' is missing a required domain.")

        # Check required environment keys
        missing_env = [env for env in skill.required_env if env not in os.environ]
        if missing_env:
            raise SkillValidationError(
                f"Skill '{skill.name}' cannot load. Missing environment variables: {missing_env}"
            )

        # Basic safety guard
        if skill.safety_level not in ("standard", "elevated", "sandbox_only"):
            raise SkillValidationError(
                f"Unrecognized safety level '{skill.safety_level}' for skill '{skill.name}'."
            )

        return True