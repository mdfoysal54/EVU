from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Iterable, List, Optional

from .models import (
    Experience,
    ExperienceFilter,
    ExperienceStatus,
)


@dataclass
class ExperienceCollector:
    """
    In-memory experience repository.

    This is the default implementation.

    Later EVU can replace/extend it with:
        PostgreSQL
        Redis
        vector storage
        object storage
        training dataset storage
    """

    experiences: List[
        Experience
    ] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._lock = RLock()

    def add(
        self,
        experience: Experience,
    ) -> Experience:

        with self._lock:
            self.experiences.append(
                experience
            )

        return experience

    def get(
        self,
        experience_id: str,
    ) -> Optional[Experience]:

        with self._lock:
            for experience in self.experiences:
                if (
                    experience.experience_id
                    == experience_id
                ):
                    return experience

        return None

    def require(
        self,
        experience_id: str,
    ) -> Experience:

        experience = self.get(
            experience_id
        )

        if experience is None:
            raise KeyError(
                f"Experience not found: "
                f"{experience_id}"
            )

        return experience

    def remove(
        self,
        experience_id: str,
    ) -> None:

        with self._lock:
            self.experiences = [
                experience
                for experience in self.experiences
                if experience.experience_id
                != experience_id
            ]

    def query(
        self,
        filters: Optional[
            ExperienceFilter
        ] = None,
    ) -> List[Experience]:

        filters = (
            filters
            or ExperienceFilter()
        )

        with self._lock:
            result = []

            for experience in self.experiences:

                if (
                    filters.agent_id is not None
                    and experience.agent_id
                    != filters.agent_id
                ):
                    continue

                if (
                    filters.model_id is not None
                    and experience.model_id
                    != filters.model_id
                ):
                    continue

                if (
                    filters.status is not None
                    and experience.status
                    != filters.status
                ):
                    continue

                if (
                    filters.task_contains
                    and filters.task_contains.lower()
                    not in experience.task.lower()
                ):
                    continue

                matched = True

                for key, value in (
                    filters.metadata.items()
                ):
                    if (
                        experience.metadata.get(
                            key
                        )
                        != value
                    ):
                        matched = False
                        break

                if not matched:
                    continue

                result.append(experience)

            if filters.limit is not None:
                result = result[
                    : filters.limit
                ]

            return list(result)

    def successful(
        self,
        limit: Optional[int] = None,
    ) -> List[Experience]:

        return self.query(
            ExperienceFilter(
                status=ExperienceStatus.SUCCESS,
                limit=limit,
            )
        )

    def failed(
        self,
        limit: Optional[int] = None,
    ) -> List[Experience]:

        return self.query(
            ExperienceFilter(
                status=ExperienceStatus.FAILED,
                limit=limit,
            )
        )

    def count(self) -> int:
        with self._lock:
            return len(self.experiences)

    def clear(self) -> None:
        with self._lock:
            self.experiences.clear()