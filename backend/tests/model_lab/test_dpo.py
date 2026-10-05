import torch

from app.model_lab.preference.loss import (
    dpo_loss,
    sequence_log_probability,
)


def test_sequence_log_probability_shape():
    logits = torch.randn(
        2,
        6,
        20,
    )

    input_ids = torch.randint(
        0,
        20,
        (2, 6),
    )

    response_mask = torch.tensor(
        [
            [0, 0, 0, 1, 1, 1],
            [0, 0, 1, 1, 1, 1],
        ],
        dtype=torch.bool,
    )

    result = sequence_log_probability(
        logits,
        input_ids,
        response_mask,
    )

    assert result.shape == (2,)


def test_dpo_loss_prefers_positive_margin():
    policy_chosen = torch.tensor(
        [0.0, 0.0]
    )

    policy_rejected = torch.tensor(
        [-2.0, -1.0]
    )

    reference_chosen = torch.tensor(
        [-1.0, -1.0]
    )

    reference_rejected = torch.tensor(
        [-1.0, -1.0]
    )

    losses, logits = dpo_loss(
        policy_chosen,
        policy_rejected,
        reference_chosen,
        reference_rejected,
        beta=0.1,
    )

    assert losses.shape == (2,)
    assert logits.shape == (2,)
    assert torch.isfinite(losses).all()
    assert torch.isfinite(logits).all()


def test_dpo_loss_backward():
    chosen = torch.tensor(
        [0.0],
        requires_grad=True,
    )

    rejected = torch.tensor(
        [-1.0],
        requires_grad=True,
    )

    ref_chosen = torch.tensor(
        [-0.5]
    )

    ref_rejected = torch.tensor(
        [-0.5]
    )

    losses, _ = dpo_loss(
        chosen,
        rejected,
        ref_chosen,
        ref_rejected,
        beta=0.1,
    )

    losses.mean().backward()

    assert chosen.grad is not None
    assert rejected.grad is not None