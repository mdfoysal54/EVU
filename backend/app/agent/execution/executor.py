import time
from typing import Any

from app.agent.execution.registry import tool_registry
from app.agent.execution.schemas import (
    ExecutionStatus,
    ToolExecutionResult,
)
from app.security.service import security_service


class ToolExecutor:

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        user=None,
    ) -> ToolExecutionResult:

        arguments = arguments or {}

        started = time.perf_counter()

        if user is not None:

            allowed, reason = (
                security_service.check_tool(
                    user,
                    tool_name,
                )
            )

            if not allowed:

                return ToolExecutionResult(
                    tool_name=tool_name,
                    status=ExecutionStatus.FAILED,
                    error=(
                        f"Permission denied: {reason}"
                    ),
                    metadata={
                        "security": "denied",
                        "latency_ms": round(
                            (
                                time.perf_counter()
                                - started
                            )
                            * 1000,
                            2,
                        ),
                    },
                )

        try:

            result = await tool_registry.execute(
                tool_name,
                arguments,
            )

            latency_ms = (
                time.perf_counter()
                - started
            ) * 1000

            return ToolExecutionResult(
                tool_name=tool_name,
                status=ExecutionStatus.COMPLETED,
                result=result,
                metadata={
                    "security": "allowed",
                    "latency_ms": round(
                        latency_ms,
                        2,
                    ),
                },
            )

        except Exception as exc:

            latency_ms = (
                time.perf_counter()
                - started
            ) * 1000

            return ToolExecutionResult(
                tool_name=tool_name,
                status=ExecutionStatus.FAILED,
                error=str(exc),
                metadata={
                    "security": "allowed",
                    "latency_ms": round(
                        latency_ms,
                        2,
                    ),
                },
            )


tool_executor = ToolExecutor()