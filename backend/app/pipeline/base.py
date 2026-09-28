from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Protocol

from .context import PipelineContext


class PipelineError(Exception):
    """Base pipeline exception."""


class PipelineCancelled(PipelineError):
    """Raised when pipeline execution is cancelled."""


class StageExecutionError(PipelineError):
    """Raised when a stage cannot execute successfully."""


class PipelineStage(Protocol):
    name: str

    def execute(self, context: PipelineContext) -> Any:
        ...


@dataclass
class PipelineResult:
    success: bool
    pipeline_id: str
    execution_id: Optional[str]

    output: Any = None
    error: Optional[str] = None

    completed_stages: List[str] = field(default_factory=list)
    failed_stage: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Pipeline:
    """
    Reusable sequential pipeline.

    Workflow nodes can execute a Pipeline instance as one unit.
    """

    name: str
    stages: List[PipelineStage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_stage(self, stage: PipelineStage) -> "Pipeline":
        self.stages.append(stage)
        return self

    def extend(self, stages: Iterable[PipelineStage]) -> "Pipeline":
        self.stages.extend(stages)
        return self

    def stage_names(self) -> List[str]:
        return [stage.name for stage in self.stages]

    def get_stage(self, name: str) -> PipelineStage:
        for stage in self.stages:
            if stage.name == name:
                return stage

        raise KeyError(f"Pipeline stage not found: {name}")

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Pipeline name cannot be empty.")

        names = self.stage_names()

        if len(names) != len(set(names)):
            raise ValueError(
                f"Duplicate pipeline stage detected: {names}"
            )

    def __len__(self) -> int:
        return len(self.stages)