from __future__ import annotations

import torch
import torch.nn.functional as F


def sequence_log_probability(
    logits: torch.Tensor,
    input_ids: torch.Tensor,
    response_mask: torch.Tensor,
) -> torch.Tensor:
    """
    Calculate the log probability of response tokens.

    logits:
        [batch, sequence, vocab]

    input_ids:
        [batch, sequence]

    response_mask:
        [batch, sequence]

    Returns:
        [batch] summed response log probabilities.
    """

    if logits.ndim != 3:
        raise ValueError(
            "logits must have shape [batch, sequence, vocab]"
        )

    if input_ids.ndim != 2:
        raise ValueError(
            "input_ids must have shape [batch, sequence]"
        )

    if response_mask.ndim != 2:
        raise ValueError(
            "response_mask must have shape [batch, sequence]"
        )

    if logits.shape[:2] != input_ids.shape:
        raise ValueError(
            "logits and input_ids sequence dimensions differ"
        )

    if response_mask.shape != input_ids.shape:
        raise ValueError(
            "response_mask and input_ids must have same shape"
        )

    # Token at position t is predicted by logits at t-1.
    shift_logits = logits[:, :-1, :]
    shift_labels = input_ids[:, 1:]
    shift_mask = response_mask[:, 1:]

    log_probs = F.log_softmax(
        shift_logits,
        dim=-1,
    )

    token_log_probs = (
        log_probs
        .gather(
            -1,
            shift_labels.unsqueeze(-1),
        )
        .squeeze(-1)
    )

    token_log_probs = token_log_probs * shift_mask.float()

    return token_log_probs.sum(dim=-1)


def dpo_loss(
    policy_chosen_logps: torch.Tensor,
    policy_rejected_logps: torch.Tensor,
    reference_chosen_logps: torch.Tensor,
    reference_rejected_logps: torch.Tensor,
    *,
    beta: float = 0.1,
    label_smoothing: float = 0.0,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Direct Preference Optimization loss.

    DPO optimizes:

        log sigma(
            beta * (
                policy_margin
                - reference_margin
            )
        )

    Returns:

        loss_per_example
        logits_per_example
    """

    if beta <= 0:
        raise ValueError(
            "beta must be greater than zero."
        )

    policy_margin = (
        policy_chosen_logps
        - policy_rejected_logps
    )

    reference_margin = (
        reference_chosen_logps
        - reference_rejected_logps
    )

    logits = beta * (
        policy_margin
        - reference_margin
    )

    positive = F.logsigmoid(logits)

    if label_smoothing > 0:
        negative = F.logsigmoid(-logits)

        losses = (
            (1.0 - label_smoothing)
            * (-positive)
            + label_smoothing
            * (-negative)
        )
    else:
        losses = -positive

    return losses, logits


def preference_accuracy(
    chosen_logps: torch.Tensor,
    rejected_logps: torch.Tensor,
) -> torch.Tensor:
    """
    Fraction of examples where chosen response
    receives higher log probability than rejected.
    """

    return (
        (chosen_logps > rejected_logps)
        .float()
        .mean()
    )