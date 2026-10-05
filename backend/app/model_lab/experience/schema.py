from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ExperienceToolCall:
    """
    One tool invocation performed during an EVU trajectory.
    """

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)

    result: Any = None

    success: bool = True

    latency_ms: float | None = None

    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExperienceStep:
    """
    One reasoning/execution step inside an EVU trajectory.
    """

    step_id: int

    action: str

    observation: str | None = None

    thought_summary: str | None = None

    tool_calls: list[ExperienceToolCall] = field(default_factory=list)

    success: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "action": self.action,
            "observation": self.observation,
            "thought_summary": self.thought_summary,
            "tool_calls": [
                call.to_dict()
                for call in self.tool_calls
            ],
            "success": self.success,
            "metadata": self.metadata,
        }


@dataclass
class ExperienceEvaluation:
    """
    Evaluation generated after an experience is completed.
    """

    correctness: float = 0.0
    usefulness: float = 0.0
    safety: float = 0.0
    tool_success: float = 0.0

    overall: float = 0.0

    passed: bool = False

    evaluator: str = "heuristic"

    reasons: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExperienceRecord:
    """
    Complete EVU interaction trajectory.

    This is intentionally model/provider agnostic.
    """

    experience_id: str

    created_at: str

    prompt: str

    response: str

    model: str = "evu"

    provider: str = "evu"

    task_type: str = "general"

    steps: list[ExperienceStep] = field(default_factory=list)

    tool_calls: list[ExperienceToolCall] = field(default_factory=list)

    success: bool = True

    error: str | None = None

    latency_ms: float | None = None

    evaluation: ExperienceEvaluation | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experience_id": self.experience_id,
            "created_at": self.created_at,
            "prompt": self.prompt,
            "response": self.response,
            "model": self.model,
            "provider": self.provider,
            "task_type": self.task_type,
            "steps": [
                step.to_dict()
                for step in self.steps
            ],
            "tool_calls": [
                call.to_dict()
                for call in self.tool_calls
            ],
            "success": self.success,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "evaluation": (
                self.evaluation.to_dict()
                if self.evaluation
                else None
            ),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ExperienceRecord":

        steps: list[ExperienceStep] = []

        for raw_step in data.get("steps", []):
            tool_calls = [
                ExperienceToolCall(**call)
                for call in raw_step.get("tool_calls", [])
            ]

            steps.append(
                ExperienceStep(
                    step_id=int(raw_step["step_id"]),
                    action=raw_step["action"],
                    observation=raw_step.get("observation"),
                    thought_summary=raw_step.get("thought_summary"),
                    tool_calls=tool_calls,
                    success=bool(
                        raw_step.get("success", True)
                    ),
                    metadata=raw_step.get(
                        "metadata",
                        {},
                    ),
                )
            )

        tool_calls = [
            ExperienceToolCall(**call)
            for call in data.get("tool_calls", [])
        ]

        evaluation_data = data.get("evaluation")

        evaluation = None

        if evaluation_data:
            evaluation = ExperienceEvaluation(
                **evaluation_data
            )

        return cls(
            experience_id=data["experience_id"],
            created_at=data.get(
                "created_at",
                utc_now(),
            ),
            prompt=data["prompt"],
            response=data["response"],
            model=data.get("model", "evu"),
            provider=data.get("provider", "evu"),
            task_type=data.get(
                "task_type",
                "general",
            ),
            steps=steps,
            tool_calls=tool_calls,
            success=bool(
                data.get("success", True)
            ),
            error=data.get("error"),
            latency_ms=data.get("latency_ms"),
            evaluation=evaluation,
            metadata=data.get(
                "metadata",
                {},
            ),
        )