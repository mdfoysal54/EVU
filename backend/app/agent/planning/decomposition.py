from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional
import uuid


@dataclass
class PlanStep:
    step_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    title: str = ""
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    tool: Optional[str] = None
    expected_output: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Plan:
    goal: str
    steps: list[PlanStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: PlanStep) -> None:
        self.steps.append(step)


class TaskDecomposer:
    """
    Deterministic planning helper.

    An LLM planner can later produce PlanStep objects using the same
    data structures.
    """

    def __init__(
        self,
        decomposer: Optional[
            Callable[[str], Iterable[Dict[str, Any]]]
        ] = None,
    ) -> None:
        self.decomposer = decomposer

    def decompose(self, goal: str) -> Plan:
        if self.decomposer is None:
            return Plan(
                goal=goal,
                steps=[
                    PlanStep(
                        title="Analyze goal",
                        description=goal,
                        expected_output="A clear understanding of the task.",
                    ),
                    PlanStep(
                        title="Execute task",
                        description="Perform the required work.",
                        dependencies=[],
                        expected_output="Task result.",
                    ),
                    PlanStep(
                        title="Verify result",
                        description="Check the produced result.",
                        expected_output="Verified result.",
                    ),
                ],
            )

        raw_steps = self.decomposer(goal)

        plan = Plan(goal=goal)

        for raw in raw_steps:
            plan.add_step(
                PlanStep(
                    title=str(raw.get("title", "")),
                    description=str(raw.get("description", "")),
                    dependencies=list(
                        raw.get("dependencies", [])
                    ),
                    tool=raw.get("tool"),
                    expected_output=raw.get(
                        "expected_output"
                    ),
                    metadata=dict(
                        raw.get("metadata", {})
                    ),
                )
            )

        return plan