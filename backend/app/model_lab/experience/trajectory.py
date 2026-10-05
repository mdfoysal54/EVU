from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .events import ExperienceEvent


@dataclass
class TrajectoryStep:
    """
    One complete action/observation cycle.
    """

    step_id: int

    action: str

    action_input: Any = None

    observation: Any = None

    tool_name: str | None = None

    tool_success: bool | None = None

    latency_ms: float | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "tool_name": self.tool_name,
            "tool_success": self.tool_success,
            "latency_ms": self.latency_ms,
            "metadata": self.metadata,
        }


@dataclass
class Trajectory:
    """
    Complete execution trajectory.
    """

    experience_id: str

    steps: list[TrajectoryStep] = field(
        default_factory=list
    )

    events: list[ExperienceEvent] = field(
        default_factory=list
    )

    completed: bool = False

    success: bool = True

    error: str | None = None

    def add_event(
        self,
        event: ExperienceEvent,
    ) -> None:

        self.events.append(event)

    def add_step(
        self,
        step: TrajectoryStep,
    ) -> None:

        self.steps.append(step)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experience_id": self.experience_id,
            "steps": [
                step.to_dict()
                for step in self.steps
            ],
            "events": [
                event.to_dict()
                for event in self.events
            ],
            "completed": self.completed,
            "success": self.success,
            "error": self.error,
        }