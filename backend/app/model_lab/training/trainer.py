from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable
import time
import torch
from torch.utils.data import DataLoader


@dataclass
class TrainingConfig:
    epochs: int = 1
    gradient_accumulation_steps: int = 1
    max_grad_norm: float | None = 1.0
    device: str = "cpu"
    log_every: int = 10
    mixed_precision: bool = False
    save_every_steps: int = 0

    def __post_init__(self) -> None:
        if self.epochs <= 0:
            raise ValueError("epochs must be positive")
        if self.gradient_accumulation_steps <= 0:
            raise ValueError("gradient_accumulation_steps must be positive")


@dataclass
class TrainingResult:
    epochs_completed: int
    global_step: int
    average_loss: float
    history: list[dict]


class Trainer:
    """Small, resumable PyTorch trainer for EVU's causal LM."""

    def __init__(
        self,
        model,
        optimizer,
        *,
        scheduler=None,
        config: TrainingConfig | None = None,
        loss_fn: Callable | None = None,
        checkpoint_manager=None,
    ) -> None:
        self.model = model
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.config = config or TrainingConfig()
        self.loss_fn = loss_fn
        self.checkpoint_manager = checkpoint_manager
        self.device = torch.device(self.config.device)
        self.model.to(self.device)
        self.global_step = 0
        self.start_epoch = 0
        amp_enabled = self.config.mixed_precision and self.device.type == "cuda"
        self.scaler = torch.amp.GradScaler("cuda", enabled=amp_enabled)

    def _compute_loss(self, batch):
        input_ids = batch.input_ids.to(self.device)
        labels = batch.labels.to(self.device)
        attention_mask = batch.attention_mask.to(self.device)

        outputs = self.model(
            input_ids,
            attention_mask=attention_mask,
            labels=labels,
        )
        if hasattr(outputs, "loss") and outputs.loss is not None:
            return outputs.loss
        if isinstance(outputs, dict) and outputs.get("loss") is not None:
            return outputs["loss"]
        if self.loss_fn is None:
            raise RuntimeError("Model did not return loss and no loss_fn was supplied.")
        logits = outputs.logits if hasattr(outputs, "logits") else outputs["logits"]
        return self.loss_fn(logits, labels)

    def train_epoch(self, dataloader: DataLoader, epoch: int) -> float:
        self.model.train()
        total_loss = 0.0
        batch_count = 0
        self.optimizer.zero_grad(set_to_none=True)
        accumulation = self.config.gradient_accumulation_steps

        for batch_index, batch in enumerate(dataloader):
            use_amp = self.config.mixed_precision and self.device.type == "cuda"
            with torch.autocast(device_type=self.device.type, enabled=use_amp):
                loss = self._compute_loss(batch)
                scaled_loss = loss / accumulation

            if use_amp:
                self.scaler.scale(scaled_loss).backward()
            else:
                scaled_loss.backward()

            final_batch = batch_index == len(dataloader) - 1
            should_step = ((batch_index + 1) % accumulation == 0) or final_batch

            if should_step:
                if self.config.max_grad_norm is not None:
                    if use_amp:
                        self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(), self.config.max_grad_norm
                    )
                if use_amp:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    self.optimizer.step()
                if self.scheduler is not None:
                    self.scheduler.step()
                self.optimizer.zero_grad(set_to_none=True)
                self.global_step += 1

            total_loss += float(loss.detach().cpu())
            batch_count += 1

            if (
                self.config.save_every_steps
                and self.checkpoint_manager
                and self.global_step
                and self.global_step % self.config.save_every_steps == 0
            ):
                self.checkpoint_manager.save(
                    name=f"step-{self.global_step:08d}.pt",
                    model=self.model,
                    optimizer=self.optimizer,
                    scheduler=self.scheduler,
                    scaler=self.scaler,
                    epoch=epoch,
                    global_step=self.global_step,
                )

        return total_loss / max(1, batch_count)

    def fit(self, dataloader: DataLoader) -> TrainingResult:
        history: list[dict] = []
        started = time.perf_counter()
        total_loss = 0.0

        for epoch in range(self.start_epoch, self.config.epochs):
            loss = self.train_epoch(dataloader, epoch)
            total_loss += loss
            record = {
                "epoch": epoch + 1,
                "loss": loss,
                "global_step": self.global_step,
                "elapsed_seconds": time.perf_counter() - started,
            }
            history.append(record)
            self.start_epoch = epoch + 1

        return TrainingResult(
            epochs_completed=self.start_epoch,
            global_step=self.global_step,
            average_loss=total_loss / max(1, len(history)),
            history=history,
        )

    def save_config(self, path) -> None:
        import json
        from pathlib import Path
        Path(path).write_text(
            json.dumps(asdict(self.config), indent=2),
            encoding="utf-8",
        )

    def resume(self, path, *, map_location=None) -> dict:
        if self.checkpoint_manager is None:
            raise RuntimeError("A CheckpointManager is required for resume().")
        state = self.checkpoint_manager.load(
            path,
            model=self.model,
            optimizer=self.optimizer,
            scheduler=self.scheduler,
            scaler=self.scaler,
            map_location=map_location or self.device,
        )
        self.global_step = int(state.get("global_step", 0))
        self.start_epoch = int(state.get("epoch", 0)) + 1
        return state