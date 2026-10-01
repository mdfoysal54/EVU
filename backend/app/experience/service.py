from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .collector import ExperienceCollector
from .exporter import ExperienceExporter
from .models import (
    Experience,
    ExperienceFilter,
    ExperienceStatus,
)
from .recorder import ExperienceRecorder
from .trajectory import Trajectory


@dataclass
class ExperienceService:
    """
    High-level EVU Experience API.

    Agent/workflow/coding modules should normally interact with this
    service rather than manipulating the collector directly.
    """

    collector: ExperienceCollector
    exporter: ExperienceExporter

    def __init__(
        self,
        collector: Optional[
            ExperienceCollector
        ] = None,
        exporter: Optional[
            ExperienceExporter
        ] = None,
    ) -> None:

        self.collector = (
            collector
            or ExperienceCollector()
        )

        self.exporter = (
            exporter
            or ExperienceExporter()
        )

    def start(
        self,
        task: str,
        *,
        agent_id: Optional[str] = None,
        model_id: Optional[str] = None,
        input_data: Optional[
            Dict[str, Any]
        ] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ExperienceRecorder:

        recorder = ExperienceRecorder()

        recorder.start(
            task,
            agent_id=agent_id,
            model_id=model_id,
            input_data=input_data,
            metadata=metadata,
        )

        return recorder

    def save(
        self,
        experience: Experience,
    ) -> Experience:

        return self.collector.add(
            experience
        )

    def finish_and_save(
        self,
        recorder: ExperienceRecorder,
        status: ExperienceStatus,
        *,
        output_data: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Experience:

        experience = recorder.finish(
            status,
            output_data=output_data,
        )

        return self.save(
            experience
        )

    def get(
        self,
        experience_id: str,
    ) -> Optional[Experience]:

        return self.collector.get(
            experience_id
        )

    def search(
        self,
        filters: Optional[
            ExperienceFilter
        ] = None,
    ) -> List[Experience]:

        return self.collector.query(
            filters
        )

    def trajectory(
        self,
        experience_id: str,
    ) -> Trajectory:

        experience = self.collector.require(
            experience_id
        )

        return Trajectory.from_experience(
            experience
        )

    def export_json(
        self,
        path: str,
        filters: Optional[
            ExperienceFilter
        ] = None,
    ) -> str:

        experiences = self.search(
            filters
        )

        return str(
            self.exporter.export_json(
                experiences,
                path,
            )
        )

    def export_training(
        self,
        path: str,
        filters: Optional[
            ExperienceFilter
        ] = None,
    ) -> str:

        experiences = self.search(
            filters
        )

        return str(
            self.exporter.export_training_jsonl(
                experiences,
                path,
            )
        )