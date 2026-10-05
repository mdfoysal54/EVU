from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from .events import ExperienceEvent
from .redaction import redact
from .schema import ExperienceRecord, ExperienceStep
from .store import ExperienceStore
from .trajectory import Trajectory, TrajectoryStep


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


@dataclass
class ExperienceRecorder:
    """
    Runtime-safe recorder for EVU.

    Usage:

        recorder = ExperienceRecorder(store)

        session = recorder.start(
            prompt="Explain Python",
            model="evu",
            provider="evu",
        )

        session.model_response(
            "Python is a programming language."
        )

        session.finish(
            success=True
        )
    """

    store: ExperienceStore

    _active: dict[str, "ExperienceSession"] = field(
        default_factory=dict
    )

    def start(
        self,
        prompt: str,
        model: str = "evu",
        provider: str = "evu",
        task_type: str = "general",
        metadata: dict[str, Any] | None = None,
    ) -> "ExperienceSession":

        experience_id = new_id("exp")

        session = ExperienceSession(
            recorder=self,
            experience_id=experience_id,
            prompt=redact(prompt),
            model=model,
            provider=provider,
            task_type=task_type,
            metadata=redact(
                metadata or {}
            ),
        )

        self._active[experience_id] = session

        session._emit(
            event_type="request_started",
            input_data=prompt,
        )

        return session

    def _complete(
        self,
        session: "ExperienceSession",
        experience: ExperienceRecord,
    ) -> None:

        self.store.append(
            experience
        )

        self._active.pop(
            session.experience_id,
            None,
        )


class ExperienceSession:
    """
    Mutable execution session.
    """

    def __init__(
        self,
        recorder: ExperienceRecorder,
        experience_id: str,
        prompt: str,
        model: str,
        provider: str,
        task_type: str,
        metadata: dict[str, Any],
    ) -> None:

        self.recorder = recorder

        self.experience_id = experience_id

        self.prompt = prompt

        self.model = model

        self.provider = provider

        self.task_type = task_type

        self.metadata = metadata

        self.started_at = time.perf_counter()

        self.steps: list[ExperienceStep] = []

        self.trajectory = Trajectory(
            experience_id=experience_id
        )

        self.response = ""

        self.error: str | None = None

        self.success = True

        self._step_counter = 0

    def _emit(
        self,
        event_type: str,
        step_id: int | None = None,
        name: str | None = None,
        input_data: Any = None,
        output_data: Any = None,
        success: bool | None = None,
        latency_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExperienceEvent:

        event = ExperienceEvent(
            event_id=new_id("event"),
            experience_id=self.experience_id,
            event_type=event_type,
            step_id=step_id,
            name=name,
            input_data=redact(input_data),
            output_data=redact(output_data),
            success=success,
            latency_ms=latency_ms,
            metadata=redact(
                metadata or {}
            ),
        )

        self.trajectory.add_event(
            event
        )

        return event

    def start_step(
        self,
        action: str,
        action_input: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:

        self._step_counter += 1

        step_id = self._step_counter

        step = TrajectoryStep(
            step_id=step_id,
            action=action,
            action_input=redact(
                action_input
            ),
            metadata=redact(
                metadata or {}
            ),
        )

        self.trajectory.add_step(
            step
        )

        self._emit(
            event_type="step_started",
            step_id=step_id,
            name=action,
            input_data=action_input,
        )

        return step_id

    def complete_step(
        self,
        step_id: int,
        observation: Any = None,
        success: bool = True,
        latency_ms: float | None = None,
    ) -> None:

        for step in self.trajectory.steps:

            if step.step_id != step_id:
                continue

            step.observation = redact(
                observation
            )

            step.tool_success = success

            step.latency_ms = latency_ms

            self._emit(
                event_type="step_completed",
                step_id=step_id,
                output_data=observation,
                success=success,
                latency_ms=latency_ms,
            )

            return

        raise ValueError(
            f"Unknown trajectory step: {step_id}"
        )

    def tool_call(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> int:

        step_id = self.start_step(
            action="tool_call",
            action_input=arguments or {},
        )

        self.trajectory.steps[-1].tool_name = name

        self._emit(
            event_type="tool_started",
            step_id=step_id,
            name=name,
            input_data=arguments or {},
        )

        return step_id

    def tool_result(
        self,
        step_id: int,
        result: Any,
        success: bool = True,
        latency_ms: float | None = None,
        error: str | None = None,
    ) -> None:

        observation = (
            error
            if error is not None
            else result
        )

        self.complete_step(
            step_id=step_id,
            observation=observation,
            success=success,
            latency_ms=latency_ms,
        )

        event_type = (
            "tool_completed"
            if success
            else "tool_failed"
        )

        self._emit(
            event_type=event_type,
            step_id=step_id,
            output_data=result,
            success=success,
            latency_ms=latency_ms,
            metadata={
                "error": error
            } if error else {},
        )

    def model_response(
        self,
        response: str,
        latency_ms: float | None = None,
    ) -> None:

        self.response = redact(
            response
        )

        self._emit(
            event_type="model_completed",
            output_data=response,
            success=True,
            latency_ms=latency_ms,
        )

    def observation(
        self,
        value: Any,
        step_id: int | None = None,
    ) -> None:

        self._emit(
            event_type="observation",
            step_id=step_id,
            output_data=value,
        )

    def fail(
        self,
        error: str,
    ) -> None:

        self.success = False

        self.error = redact(
            error
        )

        self._emit(
            event_type="request_failed",
            output_data=error,
            success=False,
        )

    def finish(
        self,
        success: bool = True,
        response: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExperienceRecord:

        if response is not None:
            self.response = redact(
                response
            )

        self.success = (
            success
            and self.success
        )

        if metadata:
            self.metadata.update(
                redact(metadata)
            )

        latency_ms = (
            time.perf_counter()
            - self.started_at
        ) * 1000.0

        self.trajectory.completed = True
        self.trajectory.success = self.success
        self.trajectory.error = self.error

        self._emit(
            event_type="request_completed",
            output_data=self.response,
            success=self.success,
            latency_ms=latency_ms,
        )

        experience_steps = []

        for trajectory_step in self.trajectory.steps:

            experience_steps.append(
                ExperienceStep(
                    step_id=trajectory_step.step_id,
                    action=trajectory_step.action,
                    observation=(
                        str(
                            trajectory_step.observation
                        )
                        if trajectory_step.observation
                        is not None
                        else None
                    ),
                    tool_calls=[],
                    success=(
                        trajectory_step.tool_success
                        if trajectory_step.tool_success
                        is not None
                        else True
                    ),
                    metadata=trajectory_step.metadata,
                )
            )

        experience = ExperienceRecord(
            experience_id=self.experience_id,
            created_at=self.trajectory.events[0].timestamp,
            prompt=self.prompt,
            response=self.response,
            model=self.model,
            provider=self.provider,
            task_type=self.task_type,
            steps=experience_steps,
            success=self.success,
            error=self.error,
            latency_ms=latency_ms,
            metadata={
                **self.metadata,
                "trajectory": self.trajectory.to_dict(),
            },
        )

        self.recorder._complete(
            self,
            experience,
        )

        return experience