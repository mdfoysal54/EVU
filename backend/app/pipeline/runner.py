from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .base import (
    Pipeline,
    PipelineCancelled,
    PipelineResult,
)
from .checkpoint import CheckpointStore
from .context import PipelineContext
from .provenance import ProvenanceTracker
from .retry import RetryPolicy


@dataclass
class PipelineRunner:
    checkpoint_store: Optional[CheckpointStore] = None
    provenance: Optional[ProvenanceTracker] = None
    default_retry: RetryPolicy = field(
        default_factory=RetryPolicy
    )

    def __post_init__(self) -> None:
        if self.checkpoint_store is None:
            self.checkpoint_store = CheckpointStore()

        if self.provenance is None:
            self.provenance = ProvenanceTracker()

    def run(
        self,
        pipeline: Pipeline,
        *,
        context: Optional[PipelineContext] = None,
        retry_policy: Optional[RetryPolicy] = None,
        checkpoint: bool = True,
    ) -> PipelineResult:

        pipeline.validate()

        if context is None:
            context = PipelineContext(
                pipeline_id=pipeline.name
            )

        policy = retry_policy or self.default_retry

        completed = []

        try:
            for stage in pipeline.stages:

                if context.cancelled:
                    raise PipelineCancelled(
                        "Pipeline was cancelled."
                    )

                context.current_stage = stage.name

                self.provenance.stage_started(
                    pipeline.name,
                    context.execution_id,
                    stage.name,
                )

                attempt = 1

                while True:
                    try:
                        result = stage.execute(context)

                        if inspect.isawaitable(result):
                            raise RuntimeError(
                                "Async stage returned an awaitable. "
                                "Use run_async() for async stages."
                            )

                        context.set(
                            f"stage:{stage.name}:result",
                            result,
                        )

                        completed.append(stage.name)

                        self.provenance.stage_completed(
                            pipeline.name,
                            context.execution_id,
                            stage.name,
                            result,
                        )

                        if checkpoint:
                            self.checkpoint_store.save(
                                checkpoint_id=(
                                    f"{context.execution_id}:"
                                    f"{stage.name}"
                                ),
                                pipeline_id=pipeline.name,
                                execution_id=context.execution_id,
                                stage_name=stage.name,
                                context=context.snapshot(),
                            )

                        break

                    except Exception as exc:
                        self.provenance.stage_failed(
                            pipeline.name,
                            context.execution_id,
                            stage.name,
                            str(exc),
                            attempt=attempt,
                        )

                        if not policy.should_retry(
                            attempt,
                            exc,
                        ):
                            raise

                        policy.wait(attempt)
                        attempt += 1

            context.finish()

            return PipelineResult(
                success=True,
                pipeline_id=pipeline.name,
                execution_id=context.execution_id,
                output=context.data.get("output"),
                completed_stages=completed,
                metadata={
                    "context": context.snapshot(),
                    "provenance": self.provenance.export(),
                },
            )

        except Exception as exc:
            context.finish()

            return PipelineResult(
                success=False,
                pipeline_id=pipeline.name,
                execution_id=context.execution_id,
                error=str(exc),
                completed_stages=completed,
                failed_stage=context.current_stage,
                metadata={
                    "context": context.snapshot(),
                    "provenance": self.provenance.export(),
                },
            )

    async def run_async(
        self,
        pipeline: Pipeline,
        *,
        context: Optional[PipelineContext] = None,
        retry_policy: Optional[RetryPolicy] = None,
        checkpoint: bool = True,
    ) -> PipelineResult:

        pipeline.validate()

        if context is None:
            context = PipelineContext(
                pipeline_id=pipeline.name
            )

        policy = retry_policy or self.default_retry

        completed = []

        try:
            for stage in pipeline.stages:

                if context.cancelled:
                    raise PipelineCancelled(
                        "Pipeline was cancelled."
                    )

                context.current_stage = stage.name

                self.provenance.stage_started(
                    pipeline.name,
                    context.execution_id,
                    stage.name,
                )

                attempt = 1

                while True:
                    try:
                        result = stage.execute(context)

                        if inspect.isawaitable(result):
                            result = await result

                        context.set(
                            f"stage:{stage.name}:result",
                            result,
                        )

                        completed.append(stage.name)

                        self.provenance.stage_completed(
                            pipeline.name,
                            context.execution_id,
                            stage.name,
                            result,
                        )

                        if checkpoint:
                            self.checkpoint_store.save(
                                checkpoint_id=(
                                    f"{context.execution_id}:"
                                    f"{stage.name}"
                                ),
                                pipeline_id=pipeline.name,
                                execution_id=context.execution_id,
                                stage_name=stage.name,
                                context=context.snapshot(),
                            )

                        break

                    except Exception as exc:
                        self.provenance.stage_failed(
                            pipeline.name,
                            context.execution_id,
                            stage.name,
                            str(exc),
                            attempt=attempt,
                        )

                        if not policy.should_retry(
                            attempt,
                            exc,
                        ):
                            raise

                        policy.wait(attempt)
                        attempt += 1

            context.finish()

            return PipelineResult(
                success=True,
                pipeline_id=pipeline.name,
                execution_id=context.execution_id,
                output=context.data.get("output"),
                completed_stages=completed,
                metadata={
                    "context": context.snapshot(),
                    "provenance": self.provenance.export(),
                },
            )

        except Exception as exc:
            context.finish()

            return PipelineResult(
                success=False,
                pipeline_id=pipeline.name,
                execution_id=context.execution_id,
                error=str(exc),
                completed_stages=completed,
                failed_stage=context.current_stage,
                metadata={
                    "context": context.snapshot(),
                    "provenance": self.provenance.export(),
                },
            )

    def resume(
        self,
        pipeline: Pipeline,
        checkpoint_id: str,
        *,
        retry_policy: Optional[RetryPolicy] = None,
    ) -> PipelineResult:

        checkpoint = self.checkpoint_store.get(
            checkpoint_id
        )

        if checkpoint is None:
            raise KeyError(
                f"Checkpoint not found: {checkpoint_id}"
            )

        context = PipelineContext.from_snapshot(
            checkpoint.context
        )

        completed_names = [
            stage.name
            for stage in pipeline.stages
            if (
                checkpoint.stage_name
                and stage.name == checkpoint.stage_name
            )
        ]

        if completed_names:
            reached = completed_names[0]
            stages = pipeline.stages
            start_index = next(
                index
                for index, stage in enumerate(stages)
                if stage.name == reached
            ) + 1

            resumed = Pipeline(
                name=pipeline.name,
                stages=stages[start_index:],
                metadata=pipeline.metadata,
            )

        else:
            resumed = pipeline

        return self.run(
            resumed,
            context=context,
            retry_policy=retry_policy,
        )