"""
EVU model training engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import torch
from torch.utils.data import DataLoader


@dataclass
class TrainingConfig:
    """
    Trainer configuration.
    """

    epochs: int = 1

    gradient_accumulation_steps: int = 1

    max_grad_norm: float | None = 1.0

    device: str = "cpu"

    log_every: int = 10

    mixed_precision: bool = False


@dataclass
class TrainingResult:
    """
    Training summary.
    """

    epochs_completed: int

    global_step: int

    average_loss: float

    history: list[dict]


class Trainer:
    """
    General-purpose PyTorch training loop for EVU.
    """

    def __init__(
        self,
        model,
        optimizer,
        *,
        scheduler=None,
        config: TrainingConfig | None = None,
        loss_fn: Callable | None = None,
    ) -> None:

        self.model = model

        self.optimizer = optimizer

        self.scheduler = scheduler

        self.config = (
            config
            or TrainingConfig()
        )

        self.loss_fn = loss_fn

        self.device = torch.device(
            self.config.device
        )

        self.model.to(self.device)

        self.global_step = 0

        self.scaler = (
            torch.amp.GradScaler(
                "cuda",
                enabled=(
                    self.config.mixed_precision
                    and self.device.type
                    == "cuda"
                ),
            )
        )

    def _compute_loss(
        self,
        batch,
    ):

        input_ids = batch.input_ids.to(
            self.device
        )

        labels = batch.labels.to(
            self.device
        )

        attention_mask = (
            batch.attention_mask.to(
                self.device
            )
        )

        outputs = self.model(
            input_ids,
            attention_mask=attention_mask,
            labels=labels,
        )

        if (
            isinstance(outputs, dict)
            and "loss" in outputs
        ):
            return outputs["loss"]

        if self.loss_fn is None:
            raise RuntimeError(
                "Model did not return loss and "
                "no loss_fn was supplied."
            )

        logits = (
            outputs["logits"]
            if isinstance(
                outputs,
                dict,
            )
            else outputs
        )

        return self.loss_fn(
            logits,
            labels,
        )

    def train_epoch(
        self,
        dataloader: DataLoader,
        epoch: int,
    ) -> float:

        self.model.train()

        total_loss = 0.0

        batch_count = 0

        self.optimizer.zero_grad(
            set_to_none=True
        )

        for batch_index, batch in enumerate(
            dataloader
        ):

            use_amp = (
                self.config.mixed_precision
                and self.device.type
                == "cuda"
            )

            with torch.autocast(
                device_type=self.device.type,
                enabled=use_amp,
            ):

                loss = self._compute_loss(
                    batch
                )

                scaled_loss = (
                    loss
                    / self.config
                    .gradient_accumulation_steps
                )

            if use_amp:
                self.scaler.scale(
                    scaled_loss
                ).backward()
            else:
                scaled_loss.backward()

            should_step = (
                (
                    batch_index + 1
                )
                % self.config
                .gradient_accumulation_steps
                == 0
            )

            if should_step:

                if (
                    self.config
                    .max_grad_norm
                    is not None
                ):

                    if use_amp:
                        self.scaler.unscale_(
                            self.optimizer
                        )

                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(),
                        self.config.max_grad_norm,
                    )

                if use_amp:
                    self.scaler.step(
                        self.optimizer
                    )

                    self.scaler.update()

                else:
                    self.optimizer.step()

                if self.scheduler is not None:
                    self.scheduler.step()

                self.optimizer.zero_grad(
                    set_to_none=True
                )

                self.global_step += 1

            total_loss += float(
                loss.detach().cpu()
            )

            batch_count += 1

        if batch_count == 0:
            return 0.0

        return total_loss / batch_count

    def fit(
        self,
        dataloader: DataLoader,
    ) -> TrainingResult:

        history = []

        total_loss = 0.0

        for epoch in range(
            self.config.epochs
        ):

            loss = self.train_epoch(
                dataloader,
                epoch,
            )

            total_loss += loss

            record = {
                "epoch": epoch + 1,
                "loss": loss,
                "global_step": (
                    self.global_step
                ),
            }

            history.append(record)

        average_loss = (
            total_loss
            / max(
                1,
                self.config.epochs,
            )
        )

        return TrainingResult(
            epochs_completed=(
                self.config.epochs
            ),
            global_step=self.global_step,
            average_loss=average_loss,
            history=history,
        )