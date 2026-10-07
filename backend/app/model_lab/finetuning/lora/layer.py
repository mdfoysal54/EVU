from __future__ import annotations

import torch
from torch import nn


class LoRALinear(nn.Module):
    def __init__(
        self,
        base: nn.Linear,
        rank: int,
        alpha: float,
        dropout: float,
    ) -> None:
        super().__init__()

        self.base = base
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank

        self.lora_dropout = nn.Dropout(dropout)

        self.lora_A = nn.Parameter(
            torch.empty(
                rank,
                base.in_features,
            )
        )

        self.lora_B = nn.Parameter(
            torch.zeros(
                base.out_features,
                rank,
            )
        )

        nn.init.kaiming_uniform_(
            self.lora_A,
            a=5**0.5,
        )

        for parameter in self.base.parameters():
            parameter.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        base_output = self.base(x)

        update = (
            self.lora_dropout(x)
            @ self.lora_A.transpose(0, 1)
            @ self.lora_B.transpose(0, 1)
        )

        return base_output + update * self.scaling