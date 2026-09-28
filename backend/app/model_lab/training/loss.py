"""
Loss functions for EVU Model Lab.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F


def causal_language_model_loss(
    logits: torch.Tensor,
    labels: torch.Tensor,
    *,
    ignore_index: int = -100,
) -> torch.Tensor:
    """
    Computes next-token prediction loss.
    """

    shift_logits = logits[
        ...,
        :-1,
        :,
    ].contiguous()

    shift_labels = labels[
        ...,
        1:,
    ].contiguous()

    return F.cross_entropy(
        shift_logits.view(
            -1,
            shift_logits.size(-1),
        ),
        shift_labels.view(-1),
        ignore_index=ignore_index,
    )


def masked_mean(
    values: torch.Tensor,
    mask: torch.Tensor,
) -> torch.Tensor:

    mask = mask.to(
        dtype=values.dtype
    )

    denominator = mask.sum().clamp_min(
        1.0
    )

    return (
        (values * mask).sum()
        / denominator
    )