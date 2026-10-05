from __future__ import annotations

from dataclasses import dataclass

import torch

from .dataset import (
    PreferenceCollator,
    PreferenceDataset,
)
from .loss import (
    sequence_log_probability,
)
from .schema import PreferenceExample


@dataclass
class PreferenceEvaluationResult:
    examples: int
    chosen_win_rate: float
    average_chosen_log_probability: float
    average_rejected_log_probability: float
    average_margin: float


@torch.no_grad()
def evaluate_preferences(
    model,
    tokenizer,
    examples: list[PreferenceExample],
    *,
    batch_size: int = 2,
    max_length: int = 1024,
    device: str = "cpu",
) -> PreferenceEvaluationResult:
    if not examples:
        raise ValueError(
            "No preference examples supplied."
        )

    dataset = PreferenceDataset(
        examples,
        tokenizer,
        max_length=max_length,
    )

    collator = PreferenceCollator(
        pad_token_id=getattr(
            tokenizer,
            "pad_token_id",
            0,
        )
    )

    loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collator,
    )

    device_obj = torch.device(device)

    model.to(device_obj)
    model.eval()

    chosen_values = []
    rejected_values = []

    for batch in loader:
        chosen_ids = (
            batch.chosen_input_ids.to(
                device_obj
            )
        )

        chosen_attention = (
            batch.chosen_attention_mask.to(
                device_obj
            )
        )

        chosen_mask = (
            batch.chosen_response_mask.to(
                device_obj
            )
        )

        rejected_ids = (
            batch.rejected_input_ids.to(
                device_obj
            )
        )

        rejected_attention = (
            batch.rejected_attention_mask.to(
                device_obj
            )
        )

        rejected_mask = (
            batch.rejected_response_mask.to(
                device_obj
            )
        )

        chosen_output = model(
            chosen_ids,
            attention_mask=chosen_attention,
        )

        rejected_output = model(
            rejected_ids,
            attention_mask=rejected_attention,
        )

        chosen_logp = (
            sequence_log_probability(
                chosen_output.logits,
                chosen_ids,
                chosen_mask,
            )
        )

        rejected_logp = (
            sequence_log_probability(
                rejected_output.logits,
                rejected_ids,
                rejected_mask,
            )
        )

        chosen_values.extend(
            chosen_logp.cpu().tolist()
        )

        rejected_values.extend(
            rejected_logp.cpu().tolist()
        )

    chosen_tensor = torch.tensor(
        chosen_values,
        dtype=torch.float32,
    )

    rejected_tensor = torch.tensor(
        rejected_values,
        dtype=torch.float32,
    )

    margin = (
        chosen_tensor
        - rejected_tensor
    )

    return PreferenceEvaluationResult(
        examples=len(chosen_values),
        chosen_win_rate=float(
            (margin > 0)
            .float()
            .mean()
        ),
        average_chosen_log_probability=float(
            chosen_tensor.mean()
        ),
        average_rejected_log_probability=float(
            rejected_tensor.mean()
        ),
        average_margin=float(
            margin.mean()
        ),
    )