from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class LoopStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


@dataclass
class AgentLoopState:
    status: LoopStatus = LoopStatus.IDLE
    iteration: int = 0
    max_iterations: int = 20

    goal: str = ""

    plan: list[Dict[str, Any]] = field(default_factory=list)
    observations: list[Dict[str, Any]] = field(default_factory=list)
    actions: list[Dict[str, Any]] = field(default_factory=list)
    results: list[Dict[str, Any]] = field(default_factory=list)

    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    error: str | None = None
    termination_reason: str | None = None

    def start(self) -> None:
        self.status = LoopStatus.RUNNING

    def next_iteration(self) -> int:
        self.iteration += 1
        return self.iteration

    def add_observation(self, observation: Dict[str, Any]) -> None:
        self.observations.append(observation)

    def add_action(self, action: Dict[str, Any]) -> None:
        self.actions.append(action)

    def add_result(self, result: Dict[str, Any]) -> None:
        self.results.append(result)

    def complete(self) -> None:
        self.status = LoopStatus.COMPLETED

    def fail(self, error: str) -> None:
        self.error = error
        self.status = LoopStatus.FAILED

    def terminate(self, reason: str) -> None:
        self.termination_reason = reason
        self.status = LoopStatus.TERMINATED

    @property
    def reached_iteration_limit(self) -> bool:
        return self.iteration >= self.max_iterations