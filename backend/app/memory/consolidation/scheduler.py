from __future__ import annotations

from dataclasses import dataclass
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from threading import RLock
from typing import Callable
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ConsolidationJob:
    id: str
    run_at: datetime
    callback: Callable[[], object]
    name: str = "memory_consolidation"
    interval_seconds: float | None = None
    enabled: bool = True


class ConsolidationScheduler:
    """Minimal scheduler.

    An external scheduler can simply call run_due().
    """

    def __init__(self) -> None:
        self._jobs: dict[
            str,
            ConsolidationJob
        ] = {}

        self._lock = RLock()

    def schedule(
        self,
        callback: Callable[[], object],
        *,
        delay_seconds: float = 0,
        name: str = "memory_consolidation",
        interval_seconds: float | None = None,
    ) -> str:
        job = ConsolidationJob(
            id=str(uuid4()),
            run_at=(
                utcnow()
                + timedelta(
                    seconds=max(
                        0,
                        delay_seconds,
                    )
                )
            ),
            callback=callback,
            name=name,
            interval_seconds=interval_seconds,
        )

        with self._lock:
            self._jobs[job.id] = job

        return job.id

    def cancel(
        self,
        job_id: str,
    ) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)

            if not job:
                return False

            job.enabled = False

            return True

    def run_due(
        self,
        now: datetime | None = None,
    ) -> list[tuple[str, object]]:
        now = now or utcnow()

        results: list[
            tuple[str, object]
        ] = []

        with self._lock:
            jobs = list(
                self._jobs.values()
            )

        for job in jobs:
            if (
                not job.enabled
                or job.run_at > now
            ):
                continue

            try:
                results.append(
                    (
                        job.id,
                        job.callback(),
                    )
                )
            finally:
                with self._lock:
                    if (
                        job.interval_seconds
                        and job.enabled
                    ):
                        job.run_at = (
                            now
                            + timedelta(
                                seconds=job.interval_seconds
                            )
                        )
                    else:
                        job.enabled = False
                        self._jobs.pop(
                            job.id,
                            None,
                        )

        return results