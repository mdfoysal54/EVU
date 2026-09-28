"""
Learning-rate scheduler utilities.
"""

from __future__ import annotations

import math

import torch


def create_cosine_scheduler(
    optimizer,
    *,
    warmup_steps: int,
    total_steps: int,
    minimum_ratio: float = 0.1,
):
    """
    Linear warmup followed by cosine decay.
    """

    if total_steps <= 0:
        raise ValueError(
            "total_steps must be positive"
        )

    if warmup_steps < 0:
        raise ValueError(
            "warmup_steps cannot be negative"
        )

    if not 0 <= minimum_ratio <= 1:
        raise ValueError(
            "minimum_ratio must be between 0 and 1"
        )

    def learning_rate_lambda(
        current_step: int,
    ) -> float:

        if (
            warmup_steps > 0
            and current_step < warmup_steps
        ):
            return (
                current_step
                / warmup_steps
            )

        if (
            total_steps
            <= warmup_steps
        ):
            return 1.0

        progress = (
            current_step
            - warmup_steps
        ) / (
            total_steps
            - warmup_steps
        )

        progress = min(
            max(progress, 0.0),
            1.0,
        )

        cosine = (
            0.5
            * (
                1
                + math.cos(
                    math.pi * progress
                )
            )
        )

        return (
            minimum_ratio
            + (
                1
                - minimum_ratio
            )
            * cosine
        )

    return torch.optim.lr_scheduler.LambdaLR(
        optimizer,
        lr_lambda=learning_rate_lambda,
    )