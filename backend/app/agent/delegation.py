from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional
import uuid


@dataclass
class DelegationRequest:
    task: str
    source_agent_id: str

    target_agent_id: Optional[str] = None
    capability: Optional[str] = None

    priority: int = 0

    context: Dict[str, Any] = field(
        default_factory=dict
    )

    request_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class DelegationResult:
    request_id: str
    success: bool

    result: Any = None
    error: Optional[str] = None

    target_agent_id: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class DelegationManager:
    def __init__(
        self,
        resolver: Optional[
            Callable[[DelegationRequest], Optional[str]]
        ] = None,
        executor: Optional[
            Callable[[str, DelegationRequest], Any]
        ] = None,
    ) -> None:
        self.resolver = resolver
        self.executor = executor

    def resolve_target(
        self,
        request: DelegationRequest,
    ) -> Optional[str]:
        if request.target_agent_id:
            return request.target_agent_id

        if self.resolver is None:
            return None

        return self.resolver(request)

    def delegate(
        self,
        request: DelegationRequest,
    ) -> DelegationResult:
        target = self.resolve_target(request)

        if target is None:
            return DelegationResult(
                request_id=request.request_id,
                success=False,
                error="No target agent could be resolved.",
            )

        if self.executor is None:
            return DelegationResult(
                request_id=request.request_id,
                success=False,
                target_agent_id=target,
                error="No delegation executor configured.",
            )

        try:
            result = self.executor(
                target,
                request,
            )

            return DelegationResult(
                request_id=request.request_id,
                success=True,
                result=result,
                target_agent_id=target,
            )

        except Exception as exc:
            return DelegationResult(
                request_id=request.request_id,
                success=False,
                target_agent_id=target,
                error=str(exc),
                metadata={
                    "error_type": type(exc).__name__,
                },
            )