from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from .state import AgentLoopState, LoopStatus
from .termination import TerminationPolicy, TerminationReason


@dataclass
class LoopStepResult:
    action: Dict[str, Any]
    result: Dict[str, Any]
    goal_reached: bool = False


class AgentLoopController:
    """
    Main think -> act -> observe loop coordinator.

    Planning, tool execution, and verification are injected through
    callables so this controller remains independent of specific LLMs.
    """

    def __init__(
        self,
        state: AgentLoopState,
        planner: Callable[[AgentLoopState], Dict[str, Any]],
        actor: Callable[[Dict[str, Any], AgentLoopState], Dict[str, Any]],
        observer: Optional[
            Callable[[Dict[str, Any], AgentLoopState], Dict[str, Any]]
        ] = None,
        termination_policy: Optional[TerminationPolicy] = None,
    ) -> None:
        self.state = state
        self.planner = planner
        self.actor = actor
        self.observer = observer
        self.termination_policy = (
            termination_policy or TerminationPolicy(
                max_iterations=state.max_iterations
            )
        )

    def run(self) -> AgentLoopState:
        self.state.start()

        while self.state.status == LoopStatus.RUNNING:
            reason = self.termination_policy.should_terminate(
                self.state
            )

            if reason is not None:
                self._terminate(reason)
                break

            try:
                self.state.next_iteration()

                action = self.planner(self.state)

                self.state.add_action(action)

                result = self.actor(
                    action,
                    self.state,
                )

                self.state.add_result(result)

                if self.observer is not None:
                    observation = self.observer(
                        result,
                        self.state,
                    )

                    self.state.add_observation(observation)

                goal_reached = bool(
                    result.get("goal_reached", False)
                )

                reason = self.termination_policy.should_terminate(
                    self.state,
                    goal_reached=goal_reached,
                )

                if reason is not None:
                    self._terminate(reason)

            except Exception as exc:
                self.state.fail(str(exc))

                reason = self.termination_policy.should_terminate(
                    self.state
                )

                if reason is not None:
                    self._terminate(reason)

        return self.state

    def stop(self, reason: str = "user_request") -> None:
        self.state.terminate(reason)

    def _terminate(
        self,
        reason: TerminationReason,
    ) -> None:
        if reason == TerminationReason.GOAL_REACHED:
            self.state.complete()
        else:
            self.state.terminate(reason.value)