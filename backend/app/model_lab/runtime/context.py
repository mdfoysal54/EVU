from __future__ import annotations

from contextvars import ContextVar

from app.model_lab.experience.recorder import (
    ExperienceSession,
)


_current_session: ContextVar[
    ExperienceSession | None
] = ContextVar(
    "evu_current_experience_session",
    default=None,
)


def set_current_session(
    session: ExperienceSession,
):
    return _current_session.set(
        session
    )


def reset_current_session(
    token,
) -> None:

    _current_session.reset(
        token
    )


def get_current_session() -> ExperienceSession | None:
    return _current_session.get()