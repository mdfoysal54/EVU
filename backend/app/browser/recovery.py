from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
import asyncio


@dataclass
class BrowserRecoveryResult:
    success: bool
    attempts: int
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class BrowserRecovery:
    def __init__(
        self,
        max_attempts: int = 3,
        retry_delay: float = 0.5,
    ) -> None:
        self.max_attempts = max(
            1,
            max_attempts,
        )

        self.retry_delay = max(
            0.0,
            retry_delay,
        )

    async def run(
        self,
        operation: Callable[[], Any],
        recover: Optional[
            Callable[[Exception, int], Any]
        ] = None,
    ) -> BrowserRecoveryResult:
        last_error: Optional[Exception] = None

        for attempt in range(
            1,
            self.max_attempts + 1,
        ):
            try:
                result = operation()

                if asyncio.iscoroutine(result):
                    result = await result

                return BrowserRecoveryResult(
                    success=True,
                    attempts=attempt,
                    result=result,
                )

            except Exception as exc:
                last_error = exc

                if recover is not None:
                    recovery_result = recover(
                        exc,
                        attempt,
                    )

                    if asyncio.iscoroutine(
                        recovery_result
                    ):
                        await recovery_result

                if attempt < self.max_attempts:
                    await asyncio.sleep(
                        self.retry_delay * attempt
                    )

        return BrowserRecoveryResult(
            success=False,
            attempts=self.max_attempts,
            error=str(last_error),
            metadata={
                "error_type": (
                    type(last_error).__name__
                    if last_error
                    else None
                )
            },
        )