from app.agent.planning.executor import plan_executor
from app.agent.planning.planner import agent_planner
from app.agent.planning.schemas import (
    PlanningRequest,
    PlanningResponse,
)


class PlanningEngine:

    async def run(
        self,
        request: PlanningRequest,
    ) -> PlanningResponse:

        plan = agent_planner.create_plan(
            goal=request.goal,
            max_steps=request.max_steps,
        )

        execution_results = []

        if request.execute:
            execution_results = await plan_executor.execute(
                plan
            )

        return PlanningResponse(
            goal=request.goal,
            plan=plan,
            execution_results=execution_results,
        )


planning_engine = PlanningEngine()