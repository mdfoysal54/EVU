from typing import Any

from app.agent.execution.executor import (
    tool_executor,
)
from app.agent.execution.registry import (
    tool_registry,
)
from app.agent.execution.schemas import (
    ExecutionStatus,
    PlanExecutionRequest,
    PlanExecutionResponse,
)
from app.agent.planning.planner import (
    agent_planner,
)


class AgentExecutionEngine:

    def __init__(self) -> None:

        self.max_tool_output_chars = 6000

    async def execute_plan(
        self,
        request: PlanExecutionRequest,
        user=None,
    ) -> PlanExecutionResponse:

        plan = agent_planner.create_plan(
            goal=request.goal,
            max_steps=request.max_steps,
        )

        if not request.execute:

            return PlanExecutionResponse(
                goal=request.goal,
                status=ExecutionStatus.PENDING,
                plan=plan.model_dump(),
                results=[],
            )

        results: list[dict[str, Any]] = []

        overall_status = (
            ExecutionStatus.COMPLETED
        )

        for step in plan.steps:

            step.status = "running"

            result: dict[str, Any]

            if step.tool:

                execution = (
                    await tool_executor.execute(
                        tool_name=step.tool,
                        arguments={},
                        user=user,
                    )
                )

                result = execution.model_dump()

                if (
                    execution.status
                    == ExecutionStatus.FAILED
                ):

                    step.status = "failed"

                    overall_status = (
                        ExecutionStatus.FAILED
                    )

                    step.error = execution.error

                    results.append(
                        {
                            "step_id": step.id,
                            "step": step.title,
                            "execution": result,
                        }
                    )

                    break

                step.status = "completed"
                step.result = execution.result

            else:

                step.status = "completed"

                step.result = {
                    "action": step.action,
                    "message": (
                        "Step prepared for "
                        "model/orchestration execution."
                    ),
                }

                result = {
                    "status": "completed",
                    "action": step.action,
                }

            results.append(
                {
                    "step_id": step.id,
                    "step": step.title,
                    "execution": result,
                }
            )

        return PlanExecutionResponse(
            goal=request.goal,
            status=overall_status,
            plan=plan.model_dump(),
            results=results,
        )

    def available_tools(
        self,
    ) -> list[dict[str, Any]]:

        return tool_registry.list_tools()


execution_engine = AgentExecutionEngine()