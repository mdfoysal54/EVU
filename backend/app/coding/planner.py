from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class CodingPlanStep:
    id: str

    title: str

    description: str

    action: str = "inspect"

    target: Optional[str] = None

    dependencies: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class CodingPlan:
    task: str

    steps: List[
        CodingPlanStep
    ] = field(
        default_factory=list
    )

    assumptions: List[str] = field(
        default_factory=list
    )

    risks: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def add(
        self,
        step: CodingPlanStep,
    ) -> "CodingPlan":

        self.steps.append(step)
        return self


class CodingPlanner:
    """
    Planner abstraction for EVU coding.

    If an LLM planner is supplied, EVU can use it.

    Otherwise this provides a deterministic baseline plan.
    """

    def __init__(
        self,
        planner: Optional[
            Callable[[str], Any]
        ] = None,
    ) -> None:

        self.planner = planner

    async def create(
        self,
        task: str,
    ) -> CodingPlan:

        if self.planner is not None:

            result = self.planner(task)

            if inspect.isawaitable(
                result
            ):
                result = await result

            if isinstance(
                result,
                CodingPlan,
            ):
                return result

            if isinstance(
                result,
                dict,
            ):
                return self.from_dict(
                    task,
                    result,
                )

        return self.baseline(task)

    def baseline(
        self,
        task: str,
    ) -> CodingPlan:

        return CodingPlan(
            task=task,
            steps=[
                CodingPlanStep(
                    id="inspect",
                    title="Inspect workspace",
                    description=(
                        "Inspect the existing project "
                        "structure and relevant files."
                    ),
                    action="inspect",
                ),
                CodingPlanStep(
                    id="implement",
                    title="Implement changes",
                    description=(
                        "Implement the required "
                        "code changes."
                    ),
                    action="implement",
                    dependencies=[
                        "inspect"
                    ],
                ),
                CodingPlanStep(
                    id="test",
                    title="Run tests",
                    description=(
                        "Run relevant automated tests."
                    ),
                    action="test",
                    dependencies=[
                        "implement"
                    ],
                ),
                CodingPlanStep(
                    id="verify",
                    title="Verify result",
                    description=(
                        "Verify that the requested "
                        "behavior is present."
                    ),
                    action="verify",
                    dependencies=[
                        "test"
                    ],
                ),
            ],
        )

    def from_dict(
        self,
        task: str,
        data: Dict[str, Any],
    ) -> CodingPlan:

        steps = []

        for index, raw in enumerate(
            data.get("steps", [])
        ):

            steps.append(
                CodingPlanStep(
                    id=str(
                        raw.get(
                            "id",
                            f"step-{index + 1}",
                        )
                    ),
                    title=str(
                        raw.get(
                            "title",
                            f"Step {index + 1}",
                        )
                    ),
                    description=str(
                        raw.get(
                            "description",
                            "",
                        )
                    ),
                    action=str(
                        raw.get(
                            "action",
                            "inspect",
                        )
                    ),
                    target=raw.get(
                        "target"
                    ),
                    dependencies=list(
                        raw.get(
                            "dependencies",
                            [],
                        )
                    ),
                    metadata=dict(
                        raw.get(
                            "metadata",
                            {},
                        )
                    ),
                )
            )

        return CodingPlan(
            task=task,
            steps=steps,
            assumptions=list(
                data.get(
                    "assumptions",
                    [],
                )
            ),
            risks=list(
                data.get(
                    "risks",
                    [],
                )
            ),
            metadata=dict(
                data.get(
                    "metadata",
                    {},
                )
            ),
        )