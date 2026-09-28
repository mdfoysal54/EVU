from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

from .state import AgentLoopState


class TerminationReason(str, Enum):
    GOAL_REACHED = "goal_reached"
    MAX_ITERATIONS = "max_iterations"
    ERROR = "error"
    USER_REQUEST = "user_request"
    NO_PROGRESS = "no_progress"
    EXTERNAL_STOP = "external_stop"


@dataclass
class TerminationPolicy:
    max_iterations: int = 20
    stop_on_error: bool = True
    no_progress_limit: int = 3

    def should_terminate(
        self,
        state: AgentLoopState,
        goal_reached: bool = False,
        external_stop: bool = False,
    ) -> Optional[TerminationReason]:

        if goal_reached:
            return TerminationReason.GOAL_REACHED

        if external_stop:
            return TerminationReason.EXTERNAL_STOP

        if state.iteration >= self.max_iterations:
            return TerminationReason.MAX_ITERATIONS

        if self.stop_on_error and state.status.value == "failed":
            return TerminationReason.ERROR

        if self._no_progress(state):
            return TerminationReason.NO_PROGRESS

        return None

    def _no_progress(self, state: AgentLoopState) -> bool:
        if self.no_progress_limit <= 0:
            return False

        if len(state.results) < self.no_progress_limit:
            return False

        recent = state.results[-self.no_progress_limit:]

        return all(
            item.get("progress") is False
            for item in recent
        )