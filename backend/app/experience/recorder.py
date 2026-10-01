from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .models import (
    EventType,
    Experience,
    ExperienceEvent,
    ExperienceStatus,
)


@dataclass
class ExperienceRecorder:
    """
    Mutable recorder used during an agent run.

    Typical lifecycle:

        recorder.start(...)
        recorder.observe(...)
        recorder.action(...)
        recorder.tool_call(...)
        recorder.tool_result(...)
        recorder.verify(...)
        recorder.finish(...)
    """

    experience: Optional[
        Experience
    ] = None

    def start(
        self,
        task: str,
        *,
        agent_id: Optional[str] = None,
        model_id: Optional[str] = None,
        input_data: Optional[
            Dict[str, Any]
        ] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Experience:

        self.experience = Experience(
            task=task,
            agent_id=agent_id,
            model_id=model_id,
            input_data=input_data or {},
            metadata=metadata or {},
        )

        self.record(
            EventType.START,
            name="experience.start",
            payload={
                "task": task,
            },
        )

        return self.experience

    def require_experience(
        self,
    ) -> Experience:

        if self.experience is None:
            raise RuntimeError(
                "Experience has not been started."
            )

        return self.experience

    def record(
        self,
        event_type: EventType | str,
        *,
        name: str = "",
        payload: Any = None,
        input_data: Any = None,
        output_data: Any = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceEvent:

        experience = self.require_experience()

        event = ExperienceEvent(
            event_type=event_type,
            name=name,
            payload=payload,
            input_data=input_data,
            output_data=output_data,
            metadata=metadata or {},
        )

        return experience.add_event(
            event
        )

    def observe(
        self,
        observation: Any,
        *,
        name: str = "observation",
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceEvent:

        return self.record(
            EventType.OBSERVATION,
            name=name,
            payload=observation,
            metadata=metadata,
        )

    def action(
        self,
        action: Any,
        *,
        name: str = "action",
        input_data: Any = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceEvent:

        return self.record(
            EventType.ACTION,
            name=name,
            payload=action,
            input_data=input_data,
            metadata=metadata,
        )

    def tool_call(
        self,
        tool_name: str,
        arguments: Any = None,
        *,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceEvent:

        return self.record(
            EventType.TOOL_CALL,
            name=tool_name,
            input_data=arguments,
            metadata=metadata,
        )

    def tool_result(
        self,
        tool_name: str,
        result: Any,
        *,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceEvent:

        return self.record(
            EventType.TOOL_RESULT,
            name=tool_name,
            output_data=result,
            metadata=metadata,
        )

    def model_call(
        self,
        model_id: str,
        prompt: Any,
        *,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceEvent:

        return self.record(
            EventType.MODEL_CALL,
            name=model_id,
            input_data=prompt,
            metadata=metadata,
        )

    def model_result(
        self,
        model_id: str,
        result: Any,
        *,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceEvent:

        return self.record(
            EventType.MODEL_RESULT,
            name=model_id,
            output_data=result,
            metadata=metadata,
        )

    def verify(
        self,
        result: Any,
        *,
        name: str = "verification",
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceEvent:

        return self.record(
            EventType.VERIFICATION,
            name=name,
            payload=result,
            metadata=metadata,
        )

    def error(
        self,
        error: Any,
        *,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceEvent:

        return self.record(
            EventType.ERROR,
            name="error",
            payload=str(error),
            metadata=metadata,
        )

    def checkpoint(
        self,
        data: Any = None,
        *,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceEvent:

        return self.record(
            EventType.CHECKPOINT,
            name="checkpoint",
            payload=data,
            metadata=metadata,
        )

    def finish(
        self,
        status: ExperienceStatus,
        *,
        output_data: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Experience:

        experience = self.require_experience()

        self.record(
            EventType.FINISH,
            name="experience.finish",
            payload={
                "status": status.value
            },
            output_data=output_data,
        )

        experience.finish(
            status,
            output_data,
        )

        return experience