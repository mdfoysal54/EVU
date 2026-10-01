from __future__ import annotations

import torch
from torch import nn


class LMHead(nn.Module):
    def __init__(self, hidden_size: int, vocab_size: int, embedding: nn.Embedding | None = None) -> None:
        super().__init__()
        self.projection = nn.Linear(hidden_size, vocab_size, bias=False)
        if embedding is not None:
            self.projection.weight = embedding.weight

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.projection(x)