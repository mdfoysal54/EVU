from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class TrainingResult:
    success: bool
    checkpoint: str | None
    metrics: dict
    error: str | None = None


class ImprovementTrainer:
    def __init__(
        self,
        sft_runner: Callable[
            [str],
            str,
        ],
        dpo_runner: Callable[
            [str, str],
            str,
        ] | None = None,
    ) -> None:
        self.sft_runner = sft_runner
        self.dpo_runner = dpo_runner

    def train_sft(
        self,
        dataset_path: str,
    ) -> TrainingResult:
        try:
            checkpoint = (
                self.sft_runner(
                    dataset_path
                )
            )

            return TrainingResult(
                success=True,
                checkpoint=checkpoint,
                metrics={
                    "stage": "sft"
                },
            )

        except Exception as exc:
            return TrainingResult(
                success=False,
                checkpoint=None,
                metrics={},
                error=str(exc),
            )

    def train_dpo(
        self,
        preference_path: str,
        reference_checkpoint: str,
    ) -> TrainingResult:
        if self.dpo_runner is None:
            return TrainingResult(
                success=False,
                checkpoint=None,
                metrics={},
                error=(
                    "DPO runner is not configured"
                ),
            )

        try:
            checkpoint = (
                self.dpo_runner(
                    preference_path,
                    reference_checkpoint,
                )
            )

            return TrainingResult(
                success=True,
                checkpoint=checkpoint,
                metrics={
                    "stage": "dpo"
                },
            )

        except Exception as exc:
            return TrainingResult(
                success=False,
                checkpoint=None,
                metrics={},
                error=str(exc),
            )