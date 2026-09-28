from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass
class RecoveryResult:
    recovered: bool
    action: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecoveryManager:
    def __init__(
        self,
        max_retries: int = 3,
    ) -> None:
        self.max_retries = max_retries
        self._attempts: Dict[str, int] = {}

    def can_retry(self, operation_id: str) -> bool:
        return self._attempts.get(operation_id, 0) < self.max_retries

    def record_failure(self, operation_id: str) -> int:
        attempt = self._attempts.get(operation_id, 0) + 1
        self._attempts[operation_id] = attempt
        return attempt

    def reset(self, operation_id: str) -> None:
        self._attempts.pop(operation_id, None)

    def recover(
        self,
        operation_id: str,
        operation: Callable[[], Any],
    ) -> RecoveryResult:
        if not self.can_retry(operation_id):
            return RecoveryResult(
                recovered=False,
                action="retry_limit_reached",
            )

        attempt = self.record_failure(operation_id)

        try:
            result = operation()

            self.reset(operation_id)

            return RecoveryResult(
                recovered=True,
                action="retry",
                metadata={
                    "attempt": attempt,
                    "result": result,
                },
            )

        except Exception as exc:
            return RecoveryResult(
                recovered=False,
                action="retry_failed",
                error=str(exc),
                metadata={
                    "attempt": attempt,
                    "error_type": type(exc).__name__,
                },
            )