"""
Parameter-efficient fine-tuning adapters.

Provides a lightweight LoRA implementation that can be
attached to Linear layers without changing the base model.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn


class LoRALinear(nn.Module):
    """
    Low-Rank Adaptation wrapper around a Linear layer.

    The original layer can be frozen while the low-rank
    matrices are trained.
    """

    def __init__(
        self,
        base_layer: nn.Linear,
        *,
        rank: int = 8,
        alpha: float = 16.0,
        dropout: float = 0.0,
    ) -> None:

        super().__init__()

        if rank <= 0:
            raise ValueError(
                "rank must be positive"
            )

        self.base = base_layer

        self.rank = rank

        self.alpha = alpha

        self.scaling = (
            alpha / rank
        )

        self.dropout = nn.Dropout(
            dropout
        )

        self.lora_a = nn.Parameter(
            torch.empty(
                rank,
                base_layer.in_features,
            )
        )

        self.lora_b = nn.Parameter(
            torch.zeros(
                base_layer.out_features,
                rank,
            )
        )

        self._initialize()

        for parameter in self.base.parameters():
            parameter.requires_grad = False

    def _initialize(self) -> None:

        nn.init.kaiming_uniform_(
            self.lora_a,
            a=math.sqrt(5),
        )

        nn.init.zeros_(
            self.lora_b
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:

        base_output = self.base(x)

        adapter = (
            self.dropout(x)
            @ self.lora_a.t()
            @ self.lora_b.t()
        )

        return (
            base_output
            + adapter * self.scaling
        )


def freeze_model(
    model: nn.Module,
) -> nn.Module:

    for parameter in model.parameters():
        parameter.requires_grad = False

    return model


def trainable_parameters(
    model: nn.Module,
):
    return [
        parameter
        for parameter in model.parameters()
        if parameter.requires_grad
    ]