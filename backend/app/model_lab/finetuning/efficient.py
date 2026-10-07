from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass
class EfficientTrainingConfig:
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    use_amp: bool = True
    amp_dtype: str = "float16"
    gradient_checkpointing: bool = False


def amp_dtype(
    config: EfficientTrainingConfig,
) -> torch.dtype:
    if config.amp_dtype == "bfloat16":
        return torch.bfloat16

    return torch.float16


class EfficientTrainer:
    """
    Small reusable trainer for EVU fine-tuning.

    Supports:
    - gradient accumulation
    - AMP
    - gradient clipping
    - checkpoint-friendly state
    """

    def __init__(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        *,
        config: EfficientTrainingConfig | None = None,
        device: str | torch.device = "cpu",
    ) -> None:
        self.model = model
        self.optimizer = optimizer
        self.config = (
            config
            or EfficientTrainingConfig()
        )
        self.device = torch.device(device)

        self.scaler = torch.amp.GradScaler(
            "cuda",
            enabled=(
                self.config.use_amp
                and self.device.type == "cuda"
                and self.config.amp_dtype == "float16"
            ),
        )

        self.global_step = 0

    def _autocast(self):
        enabled = (
            self.config.use_amp
            and self.device.type == "cuda"
        )

        return torch.autocast(
            device_type=self.device.type,
            dtype=amp_dtype(self.config),
            enabled=enabled,
        )

    def train_batch(
        self,
        input_ids: torch.Tensor,
        labels: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
    ) -> float:
        self.model.train()

        input_ids = input_ids.to(
            self.device
        )
        labels = labels.to(
            self.device
        )

        if attention_mask is not None:
            attention_mask = attention_mask.to(
                self.device
            )

        with self._autocast():
            output = self.model(
                input_ids,
                attention_mask=attention_mask,
                labels=labels,
            )

            if output.loss is None:
                raise RuntimeError(
                    "Model did not return a loss."
                )

            loss = output.loss / (
                self.config.gradient_accumulation_steps
            )

        if self.scaler.is_enabled():
            self.scaler.scale(loss).backward()
        else:
            loss.backward()

        should_step = (
            (self.global_step + 1)
            % self.config.gradient_accumulation_steps
            == 0
        )

        if should_step:
            if self.scaler.is_enabled():
                self.scaler.unscale_(
                    self.optimizer
                )

            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                self.config.max_grad_norm,
            )

            if self.scaler.is_enabled():
                self.scaler.step(
                    self.optimizer
                )
                self.scaler.update()
            else:
                self.optimizer.step()

            self.optimizer.zero_grad(
                set_to_none=True
            )

        self.global_step += 1

        return float(
            output.loss.detach().cpu()
        )

    def state_dict(self) -> dict:
        return {
            "global_step": self.global_step,
            "optimizer": self.optimizer.state_dict(),
            "scaler": self.scaler.state_dict(),
        }

    def load_state_dict(
        self,
        state: dict,
    ) -> None:
        self.global_step = int(
            state.get(
                "global_step",
                0,
            )
        )

        if "optimizer" in state:
            self.optimizer.load_state_dict(
                state["optimizer"]
            )

        if "scaler" in state:
            self.scaler.load_state_dict(
                state["scaler"]
            )