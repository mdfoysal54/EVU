"""
Preference-learning data structures.

This module provides the data layer for future DPO/IPO/
preference-optimization implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..tokenizer import EVUTokenizer


@dataclass
class PreferenceExample:
    """
    Preference pair.

    chosen = preferred response
    rejected = less-preferred response
    """

    prompt: str

    chosen: str

    rejected: str


@dataclass
class TokenizedPreferenceExample:
    """
    Tokenized preference pair.
    """

    prompt_ids: list[int]

    chosen_ids: list[int]

    rejected_ids: list[int]


class PreferenceDataset:
    """
    Tokenized preference dataset.
    """

    def __init__(
        self,
        examples: Iterable[
            PreferenceExample
        ],
        tokenizer: EVUTokenizer,
        *,
        max_length: int | None = None,
    ) -> None:

        self.examples = []

        for example in examples:

            prompt_ids = tokenizer.encode(
                example.prompt
            )

            chosen_ids = tokenizer.encode(
                example.chosen
            )

            rejected_ids = tokenizer.encode(
                example.rejected
            )

            if max_length is not None:

                prompt_ids = prompt_ids[
                    :max_length
                ]

                chosen_ids = chosen_ids[
                    :max_length
                ]

                rejected_ids = rejected_ids[
                    :max_length
                ]

            self.examples.append(
                TokenizedPreferenceExample(
                    prompt_ids=prompt_ids,
                    chosen_ids=chosen_ids,
                    rejected_ids=rejected_ids,
                )
            )

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(
        self,
        index: int,
    ) -> TokenizedPreferenceExample:

        return self.examples[index]


def dpo_loss(
    chosen_logps,
    rejected_logps,
    reference_chosen_logps,
    reference_rejected_logps,
    *,
    beta: float = 0.1,
):
    """
    Direct Preference Optimization loss.

    All arguments should contain summed/log-probability
    values for their corresponding response sequences.
    """

    import torch

    policy_margin = (
        chosen_logps
        - rejected_logps
    )

    reference_margin = (
        reference_chosen_logps
        - reference_rejected_logps
    )

    logits = beta * (
        policy_margin
        - reference_margin
    )

    return -torch.nn.functional.logsigmoid(
        logits
    ).mean()