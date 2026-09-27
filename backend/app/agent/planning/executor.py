from typing import Any

from app.agent.planning.schemas import (
    AgentPlan,
    PlanStepStatus,
)


class PlanExecutor:
    """
    Executes a plan at the orchestration level.

    This first implementation does not automatically execute
    arbitrary tools. It prepares a safe execution state that
    later tool/LLM execution layers can consume.
    """

    async def execute(
        self,
        plan: AgentPlan,
    ) -> list[dict[str, Any]]:

        results: list[dict[str, Any]] = []

        for step in plan.steps:

            missing_dependencies = []

            for dependency_id in step.depends_on:
                dependency = next(
                    (
                        item
                        for item in plan.steps
                        if item.id == dependency_id
                    ),
                    None,
                )

                if dependency is None:
                    missing_dependencies.append(
                        dependency_id
                    )
                    continue

                if dependency.status != PlanStepStatus.COMPLETED:
                    missing_dependencies.append(
                        dependency_id
                    )

            if missing_dependencies:
                step.status = PlanStepStatus.SKIPPED
                step.error = (
                    "Dependencies not completed: "
                    + ", ".join(
                        str(item)
                        for item in missing_dependencies
                    )
                )

                results.append(
                    {
                        "step_id": step.id,
                        "status": step.status.value,
                        "error": step.error,
                    }
                )

                continue

            step.status = PlanStepStatus.RUNNING

            try:
                result = await self._execute_action(
                    step.action,
                    step.description,
                )

                step.result = result
                step.status = PlanStepStatus.COMPLETED

                results.append(
                    {
                        "step_id": step.id,
                        "status": step.status.value,
                        "result": result,
                    }
                )

            except Exception as exc:
                step.status = PlanStepStatus.FAILED
                step.error = str(exc)

                results.append(
                    {
                        "step_id": step.id,
                        "status": step.status.value,
                        "error": step.error,
                    }
                )

                break

        return results

    async def _execute_action(
        self,
        action: str,
        description: str,
    ) -> dict[str, str]:

        """
        Safe placeholder execution.

        Actual tool execution will be connected to the EVU
        tool registry in the next agent evolution.
        """

        return {
            "action": action,
            "message": (
                "Execution context prepared. "
                "Tool/model execution can now consume this step."
            ),
            "description": description,
        }


plan_executor = PlanExecutor()