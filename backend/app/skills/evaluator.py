from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional

from .discovery import SkillDescriptor


@dataclass
class SkillEvaluation:
    skill_name: str

    score: float
    passed: bool

    checks: Dict[str, bool] = field(
        default_factory=dict
    )

    metrics: Dict[str, float] = field(
        default_factory=dict
    )

    errors: List[str] = field(
        default_factory=list
    )


class SkillEvaluator:
    def __init__(
        self,
        threshold: float = 0.7,
    ) -> None:
        self.threshold = threshold

    def evaluate(
        self,
        skill: SkillDescriptor,
        checks: Dict[
            str,
            Callable[[SkillDescriptor], bool],
        ],
    ) -> SkillEvaluation:
        results: Dict[str, bool] = {}
        errors: list[str] = []

        for name, check in checks.items():
            try:
                results[name] = bool(check(skill))
            except Exception as exc:
                results[name] = False
                errors.append(
                    f"{name}: {exc}"
                )

        if not results:
            score = 0.0
        else:
            score = sum(
                results.values()
            ) / len(results)

        return SkillEvaluation(
            skill_name=skill.name,
            score=score,
            passed=score >= self.threshold
            and not errors,
            checks=results,
            metrics={
                "check_count": float(len(results)),
            },
            errors=errors,
        )

    @staticmethod
    def default_checks() -> Dict[
        str,
        Callable[[SkillDescriptor], bool],
    ]:
        return {
            "has_name": lambda skill: bool(
                skill.name.strip()
            ),
            "has_description": lambda skill: bool(
                skill.description.strip()
            ),
            "has_version": lambda skill: bool(
                skill.version.strip()
            ),
        }