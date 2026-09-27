import re

from app.agent.planning.schemas import (
    AgentPlan,
    PlanStep,
    PlanStepStatus,
)


class AgentPlanner:
    """
    Deterministic planning engine.

    The first version intentionally uses predictable rules
    instead of asking an LLM to generate executable code.
    """

    def create_plan(
        self,
        goal: str,
        max_steps: int = 8,
    ) -> AgentPlan:

        goal_clean = goal.strip()

        steps: list[PlanStep] = []

        lower = goal_clean.lower()

        research_words = [
            "research",
            "find",
            "search",
            "investigate",
            "compare",
            "latest",
        ]

        writing_words = [
            "write",
            "draft",
            "create",
            "prepare",
            "compose",
        ]

        coding_words = [
            "code",
            "build",
            "develop",
            "implement",
            "debug",
        ]

        if any(word in lower for word in research_words):
            steps.extend(
                [
                    PlanStep(
                        id=1,
                        title="Understand the research goal",
                        description=(
                            "Identify the exact information "
                            "needed to answer the request."
                        ),
                        action="analyze",
                    ),
                    PlanStep(
                        id=2,
                        title="Gather information",
                        description=(
                            "Collect relevant information "
                            "using available research tools."
                        ),
                        action="research",
                        tool="web_research",
                        depends_on=[1],
                    ),
                    PlanStep(
                        id=3,
                        title="Evaluate information",
                        description=(
                            "Compare findings and identify "
                            "conflicts or missing information."
                        ),
                        action="evaluate",
                        depends_on=[2],
                    ),
                    PlanStep(
                        id=4,
                        title="Produce final answer",
                        description=(
                            "Synthesize the findings into "
                            "one clear response."
                        ),
                        action="synthesize",
                        depends_on=[3],
                    ),
                ]
            )

        elif any(word in lower for word in coding_words):
            steps.extend(
                [
                    PlanStep(
                        id=1,
                        title="Understand requirements",
                        description=(
                            "Break the software request into "
                            "clear implementation requirements."
                        ),
                        action="analyze",
                    ),
                    PlanStep(
                        id=2,
                        title="Design solution",
                        description=(
                            "Determine architecture, files, "
                            "components and dependencies."
                        ),
                        action="design",
                        depends_on=[1],
                    ),
                    PlanStep(
                        id=3,
                        title="Implement solution",
                        description=(
                            "Implement the requested software "
                            "changes."
                        ),
                        action="code",
                        depends_on=[2],
                    ),
                    PlanStep(
                        id=4,
                        title="Review implementation",
                        description=(
                            "Check the implementation for "
                            "errors and missing requirements."
                        ),
                        action="evaluate",
                        depends_on=[3],
                    ),
                ]
            )

        elif any(word in lower for word in writing_words):
            steps.extend(
                [
                    PlanStep(
                        id=1,
                        title="Understand writing requirements",
                        description=(
                            "Determine audience, purpose, "
                            "tone and required content."
                        ),
                        action="analyze",
                    ),
                    PlanStep(
                        id=2,
                        title="Create draft",
                        description=(
                            "Produce a first version based "
                            "on the requirements."
                        ),
                        action="write",
                        depends_on=[1],
                    ),
                    PlanStep(
                        id=3,
                        title="Review draft",
                        description=(
                            "Check clarity, grammar, structure "
                            "and completeness."
                        ),
                        action="evaluate",
                        depends_on=[2],
                    ),
                    PlanStep(
                        id=4,
                        title="Finalize response",
                        description=(
                            "Produce the polished final version."
                        ),
                        action="synthesize",
                        depends_on=[3],
                    ),
                ]
            )

        else:
            steps.extend(
                [
                    PlanStep(
                        id=1,
                        title="Understand the request",
                        description=(
                            "Analyze the user's objective "
                            "and constraints."
                        ),
                        action="analyze",
                    ),
                    PlanStep(
                        id=2,
                        title="Determine the solution",
                        description=(
                            "Reason about the best approach "
                            "to solve the request."
                        ),
                        action="reason",
                        depends_on=[1],
                    ),
                    PlanStep(
                        id=3,
                        title="Review the result",
                        description=(
                            "Check the result against the "
                            "original objective."
                        ),
                        action="evaluate",
                        depends_on=[2],
                    ),
                    PlanStep(
                        id=4,
                        title="Produce final answer",
                        description=(
                            "Return the final response."
                        ),
                        action="synthesize",
                        depends_on=[3],
                    ),
                ]
            )

        steps = steps[:max_steps]

        for index, step in enumerate(steps, start=1):
            step.id = index

            if index > 1:
                valid_dependencies = [
                    dependency
                    for dependency in step.depends_on
                    if dependency < index
                ]

                step.depends_on = valid_dependencies

        return AgentPlan(
            goal=goal_clean,
            steps=steps,
            max_steps=max_steps,
            metadata={
                "planner": "evu_rule_based_planner",
                "step_count": len(steps),
            },
        )


agent_planner = AgentPlanner()