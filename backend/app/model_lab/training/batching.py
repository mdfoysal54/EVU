"""
Batch collation utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

try:
    import torch  # type: ignore[import-not-found]
except ImportError:
    torch = None  # type: ignore[assignment]

if TYPE_CHECKING:
    import torch


@dataclass
class Batch:
    """
    Training batch.
    """

    input_ids: torch.Tensor | Any

    labels: torch.Tensor | Any

    attention_mask: torch.Tensor | Any


class CausalBatchCollator:
    """
    Pads variable-length token sequences.

    Labels use -100 for padding so PyTorch cross entropy
    ignores those positions.
    """

    def __init__(
        self,
        pad_token_id: int,
    ) -> None:

        self.pad_token_id = pad_token_id

    def __call__(
        self,
        examples,
    ) -> Batch:

        if not examples:
            raise ValueError(
                "Cannot collate an empty batch."
            )

        if torch is None:
            raise RuntimeError(
                "Batch collation requires PyTorch. "
                "Install it with: pip install torch"
            )

        max_length = max(
            len(example.input_ids)
            for example in examples
        )

        input_ids = []
        labels = []
        attention_masks = []

        for example in examples:

            ids = list(
                example.input_ids
            )

            example_labels = (
                list(example.labels)
                if example.labels is not None
                else list(ids)
            )

            padding = (
                max_length
                - len(ids)
            )

            input_ids.append(
                ids
                + [
                    self.pad_token_id
                ]
                * padding
            )

            labels.append(
                example_labels
                + [-100] * padding
            )

            attention_masks.append(
                [1] * len(ids)
                + [0] * padding
            )

        return Batch(
            input_ids=torch.tensor(
                input_ids,
                dtype=torch.long,
            ),
            labels=torch.tensor(
                labels,
                dtype=torch.long,
            ),
            attention_mask=torch.tensor(
                attention_masks,
                dtype=torch.bool,
            ),
        )