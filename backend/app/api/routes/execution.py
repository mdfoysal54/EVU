from fastapi import APIRouter, Depends, HTTPException

from app.agent.execution.engine import (
    execution_engine,
)
from app.agent.execution.executor import (
    tool_executor,
)
from app.agent.execution.schemas import (
    PlanExecutionRequest,
    PlanExecutionResponse,
    ToolExecutionRequest,
    ToolExecutionResult,
)
from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/execution",
    tags=["EVU Agent Execution"],
)


@router.get("/tools")
async def list_tools(
    current_user=Depends(get_current_user),
):
    return {
        "tools": execution_engine.available_tools()
    }


@router.post(
    "/tool",
    response_model=ToolExecutionResult,
)
async def execute_tool(
    request: ToolExecutionRequest,
    current_user=Depends(get_current_user),
):
    result = await tool_executor.execute(
        tool_name=request.tool_name,
        arguments=request.arguments,
        user=current_user,
    )

    if result.status.value == "failed":
        raise HTTPException(
            status_code=403
            if result.metadata.get("security") == "denied"
            else 400,
            detail=result.error,
        )

    return result


@router.post(
    "/plan",
    response_model=PlanExecutionResponse,
)
async def execute_plan(
    request: PlanExecutionRequest,
    current_user=Depends(get_current_user),
):
    try:
        return await execution_engine.execute_plan(
            request,
            user=current_user,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Execution failed: {exc}",
        ) from exc