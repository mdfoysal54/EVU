"""
Optimizer construction utilities.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class OptimizerConfig:
    """
    AdamW configuration.
    """

    learning_rate: float = 3e-4

    weight_decay: float = 0.01

    betas: tuple[
        float,
        float,
    ] = (
        0.9,
        0.95,
    )

    eps: float = 1e-8


def create_optimizer(
    model,
    config: OptimizerConfig | None = None,
):
    """
    Creates an AdamW optimizer.
    """

    config = (
        config
        or OptimizerConfig()
    )

    return torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        betas=config.betas,
        eps=config.eps,
        weight_decay=config.weight_decay,
    )