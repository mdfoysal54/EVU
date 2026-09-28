from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple, Type


@dataclass
class RetryPolicy:
    """
    Controls stage retry behavior.

    max_attempts=1 means no retry.
    """

    max_attempts: int = 1
    initial_delay: float = 0.0
    backoff_factor: float = 2.0
    max_delay: float = 30.0

    retry_exceptions: Tuple[Type[BaseException], ...] = (
        Exception,
    )

    jitter: Optional[Callable[[float], float]] = None

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")

        if self.initial_delay < 0:
            raise ValueError("initial_delay cannot be negative")

        if self.backoff_factor < 1:
            raise ValueError("backoff_factor must be >= 1")

        if self.max_delay < 0:
            raise ValueError("max_delay cannot be negative")

    def should_retry(
        self,
        attempt: int,
        error: BaseException,
    ) -> bool:
        if attempt >= self.max_attempts:
            return False

        return isinstance(error, self.retry_exceptions)

    def delay_for(self, attempt: int) -> float:
        """
        attempt=1 -> initial_delay
        attempt=2 -> initial_delay * backoff_factor
        """
        if self.initial_delay <= 0:
            return 0.0

        delay = self.initial_delay * (
            self.backoff_factor ** max(0, attempt - 1)
        )

        delay = min(delay, self.max_delay)

        if self.jitter:
            delay = max(0.0, self.jitter(delay))

        return delay

    def wait(self, attempt: int) -> None:
        delay = self.delay_for(attempt)

        if delay > 0:
            time.sleep(delay)