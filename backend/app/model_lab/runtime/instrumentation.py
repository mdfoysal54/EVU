from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Iterator

from app.model_lab.experience.recorder import (
    ExperienceRecorder,
)

from .context import (
    reset_current_session,
    set_current_session,
)


@contextmanager
def record_request(
    recorder: ExperienceRecorder,
    prompt: str,
    model: str = "evu",
    provider: str = "evu",
    task_type: str = "general",
    metadata: dict[str, Any] | None = None,
) -> Iterator:

    session = recorder.start(
        prompt=prompt,
        model=model,
        provider=provider,
        task_type=task_type,
        metadata=metadata,
    )

    token = set_current_session(
        session
    )

    try:

        yield session

    except Exception as exc:

        session.fail(
            str(exc)
        )

        session.finish(
            success=False
        )

        raise

    finally:

        reset_current_session(
            token
        )