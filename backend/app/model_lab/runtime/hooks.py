from __future__ import annotations

from typing import Any

from .context import get_current_session


def record_step(
    action: str,
    action_input: Any = None,
) -> int | None:

    session = get_current_session()

    if session is None:
        return None

    return session.start_step(
        action=action,
        action_input=action_input,
    )


def record_observation(
    value: Any,
    step_id: int | None = None,
) -> None:

    session = get_current_session()

    if session is None:
        return

    session.observation(
        value=value,
        step_id=step_id,
    )


def record_tool_start(
    name: str,
    arguments: dict[str, Any] | None = None,
) -> int | None:

    session = get_current_session()

    if session is None:
        return None

    return session.tool_call(
        name=name,
        arguments=arguments,
    )


def record_tool_result(
    step_id: int | None,
    result: Any,
    success: bool = True,
    latency_ms: float | None = None,
    error: str | None = None,
) -> None:

    session = get_current_session()

    if session is None or step_id is None:
        return

    session.tool_result(
        step_id=step_id,
        result=result,
        success=success,
        latency_ms=latency_ms,
        error=error,
    )


def record_model_response(
    response: str,
    latency_ms: float | None = None,
) -> None:

    session = get_current_session()

    if session is None:
        return

    session.model_response(
        response=response,
        latency_ms=latency_ms,
    )