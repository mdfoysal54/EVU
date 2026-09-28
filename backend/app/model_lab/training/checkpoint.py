"""
Model training checkpoint management.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch


@dataclass
class CheckpointState:
    """
    Metadata associated with a checkpoint.
    """

    epoch: int

    global_step: int

    best_loss: float | None = None


class CheckpointManager:
    """
    Saves and restores model training state.
    """

    def __init__(
        self,
        directory: str | Path,
    ) -> None:

        self.directory = Path(
            directory
        )

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        *,
        name: str,
        model,
        optimizer=None,
        scheduler=None,
        scaler=None,
        epoch: int = 0,
        global_step: int = 0,
        best_loss: float | None = None,
        extra: dict[str, Any] | None = None,
    ) -> Path:

        state = {
            "model_state_dict": (
                model.state_dict()
            ),
            "epoch": epoch,
            "global_step": global_step,
            "best_loss": best_loss,
            "extra": extra or {},
        }

        if optimizer is not None:
            state[
                "optimizer_state_dict"
            ] = optimizer.state_dict()

        if scheduler is not None:
            state[
                "scheduler_state_dict"
            ] = scheduler.state_dict()

        if scaler is not None:
            state[
                "scaler_state_dict"
            ] = scaler.state_dict()

        path = self.directory / name

        if path.suffix != ".pt":
            path = path.with_suffix(
                ".pt"
            )

        torch.save(
            state,
            path,
        )

        return path

    def load(
        self,
        path: str | Path,
        *,
        model,
        optimizer=None,
        scheduler=None,
        scaler=None,
        map_location="cpu",
    ) -> dict[str, Any]:

        checkpoint = torch.load(
            path,
            map_location=map_location,
        )

        model.load_state_dict(
            checkpoint[
                "model_state_dict"
            ]
        )

        if (
            optimizer is not None
            and "optimizer_state_dict"
            in checkpoint
        ):
            optimizer.load_state_dict(
                checkpoint[
                    "optimizer_state_dict"
                ]
            )

        if (
            scheduler is not None
            and "scheduler_state_dict"
            in checkpoint
        ):
            scheduler.load_state_dict(
                checkpoint[
                    "scheduler_state_dict"
                ]
            )

        if (
            scaler is not None
            and "scaler_state_dict"
            in checkpoint
        ):
            scaler.load_state_dict(
                checkpoint[
                    "scaler_state_dict"
                ]
            )

        return checkpoint