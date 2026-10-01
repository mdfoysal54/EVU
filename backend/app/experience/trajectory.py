from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from .models import (
    EventType,
    Experience,
    ExperienceEvent,
    ExperienceStatus,
)


@dataclass
class TrajectoryStep:
    """
    Normalized representation of one agent step.

    Useful for training/evaluation later.
    """

    index: int

    event_type: str
    name: str

    input_data: Any = None
    output_data: Any = None
    payload: Any = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class Trajectory:
    """
    Read-oriented representation of an Experience.

    Experience is the persisted object.
    Trajectory is the normalized sequence used by
    training, evaluation and analysis.
    """

    experience_id: str

    task: str

    steps: List[TrajectoryStep] = field(
        default_factory=list
    )

    status: str = ExperienceStatus.RUNNING.value

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_experience(
        cls,
        experience: Experience,
    ) -> "Trajectory":

        steps = [
            TrajectoryStep(
                index=index,
                event_type=(
                    event.event_type.value
                    if isinstance(
                        event.event_type,
                        EventType,
                    )
                    else str(event.event_type)
                ),
                name=event.name,
                input_data=event.input_data,
                output_data=event.output_data,
                payload=event.payload,
                metadata=dict(event.metadata),
            )
            for index, event in enumerate(
                experience.events
            )
        ]

        return cls(
            experience_id=experience.experience_id,
            task=experience.task,
            steps=steps,
            status=experience.status.value,
            metadata=dict(experience.metadata),
        )

    def filter_events(
        self,
        event_type: str,
    ) -> List[TrajectoryStep]:

        return [
            step
            for step in self.steps
            if step.event_type == event_type
        ]

    def actions(self) -> List[TrajectoryStep]:
        return self.filter_events(
            EventType.ACTION.value
        )

    def tool_calls(self) -> List[TrajectoryStep]:
        return self.filter_events(
            EventType.TOOL_CALL.value
        )

    def observations(self) -> List[TrajectoryStep]:
        return self.filter_events(
            EventType.OBSERVATION.value
        )

    def verification_steps(
        self,
    ) -> List[TrajectoryStep]:

        return self.filter_events(
            EventType.VERIFICATION.value
        )

    def to_training_record(
        self,
    ) -> Dict[str, Any]:

        return {
            "experience_id": self.experience_id,
            "task": self.task,
            "status": self.status,
            "steps": [
                {
                    "index": step.index,
                    "event_type": step.event_type,
                    "name": step.name,
                    "input": step.input_data,
                    "output": step.output_data,
                    "payload": step.payload,
                    "metadata": step.metadata,
                }
                for step in self.steps
            ],
            "metadata": self.metadata,
        }


def build_trajectory(
    experience: Experience,
) -> Trajectory:

    return Trajectory.from_experience(
        experience
    )