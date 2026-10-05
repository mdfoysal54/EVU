from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import torch
from torch.utils.data import Dataset

from .schema import PreferenceExample


@dataclass
class EncodedPreferenceExample:
    chosen_input_ids: list[int]
    chosen_response_mask: list[int]

    rejected_input_ids: list[int]
    rejected_response_mask: list[int]

    metadata: dict


class PreferenceDataset(Dataset):
    """
    Tokenized preference dataset.

    Only response tokens participate in DPO sequence scoring.
    Prompt tokens are masked out.
    """

    def __init__(
        self,
        examples: Sequence[PreferenceExample],
        tokenizer,
        *,
        max_length: int = 1024,
    ) -> None:
        self.items: list[EncodedPreferenceExample] = []

        for example in examples:
            encoded = self._encode(
                example,
                tokenizer,
                max_length,
            )

            if encoded is not None:
                self.items.append(encoded)

        if not self.items:
            raise ValueError(
                "PreferenceDataset contains no usable examples."
            )

    @staticmethod
    def _build_prompt(
        prompt: str,
    ) -> str:
        return (
            f"User: {prompt.strip()}\n"
            "Assistant: "
        )

    @classmethod
    def _encode_response(
        cls,
        prompt: str,
        response: str,
        tokenizer,
        max_length: int,
    ) -> tuple[list[int], list[int]] | None:
        prefix = cls._build_prompt(prompt)

        prefix_ids = tokenizer.encode(
            prefix,
            add_special_tokens=True,
        )

        response_ids = tokenizer.encode(
            response.strip(),
            add_special_tokens=False,
        )

        eos_id = getattr(
            tokenizer,
            "eos_token_id",
            None,
        )

        if eos_id is not None:
            response_ids = [
                *response_ids,
                int(eos_id),
            ]

        if not response_ids:
            return None

        total_length = (
            len(prefix_ids)
            + len(response_ids)
        )

        if total_length > max_length:
            response_budget = min(
                len(response_ids),
                max_length,
            )

            prefix_budget = max_length - response_budget

            if prefix_budget > 0:
                prefix_ids = prefix_ids[
                    -prefix_budget:
                ]
            else:
                prefix_ids = []

            response_ids = response_ids[
                :response_budget
            ]

        input_ids = [
            *prefix_ids,
            *response_ids,
        ]

        response_mask = (
            [0] * len(prefix_ids)
            + [1] * len(response_ids)
        )

        if len(input_ids) < 2:
            return None

        return (
            input_ids,
            response_mask,
        )

    @classmethod
    def _encode(
        cls,
        example: PreferenceExample,
        tokenizer,
        max_length: int,
    ) -> EncodedPreferenceExample | None:
        chosen = cls._encode_response(
            example.prompt,
            example.chosen,
            tokenizer,
            max_length,
        )

        rejected = cls._encode_response(
            example.prompt,
            example.rejected,
            tokenizer,
            max_length,
        )

        if chosen is None or rejected is None:
            return None

        return EncodedPreferenceExample(
            chosen_input_ids=chosen[0],
            chosen_response_mask=chosen[1],
            rejected_input_ids=rejected[0],
            rejected_response_mask=rejected[1],
            metadata=example.metadata or {},
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(
        self,
        index: int,
    ) -> EncodedPreferenceExample:
        return self.items[index]


@dataclass
class PreferenceBatch:
    chosen_input_ids: torch.Tensor
    chosen_attention_mask: torch.Tensor
    chosen_response_mask: torch.Tensor

    rejected_input_ids: torch.Tensor
    rejected_attention_mask: torch.Tensor
    rejected_response_mask: torch.Tensor


class PreferenceCollator:
    def __init__(
        self,
        pad_token_id: int = 0,
    ) -> None:
        self.pad_token_id = int(
            pad_token_id
        )

    @staticmethod
    def _pad(
        sequences: list[list[int]],
        pad_value: int,
    ) -> torch.Tensor:
        max_length = max(
            len(sequence)
            for sequence in sequences
        )

        return torch.tensor(
            [
                sequence
                + [pad_value]
                * (
                    max_length
                    - len(sequence)
                )
                for sequence in sequences
            ],
            dtype=torch.long,
        )

    @staticmethod
    def _pad_mask(
        masks: list[list[int]],
    ) -> torch.Tensor:
        max_length = max(
            len(mask)
            for mask in masks
        )

        return torch.tensor(
            [
                mask
                + [0]
                * (
                    max_length
                    - len(mask)
                )
                for mask in masks
            ],
            dtype=torch.bool,
        )

    def __call__(
        self,
        items: Sequence[
            EncodedPreferenceExample
        ],
    ) -> PreferenceBatch:
        chosen_ids = [
            item.chosen_input_ids
            for item in items
        ]

        chosen_masks = [
            item.chosen_response_mask
            for item in items
        ]

        rejected_ids = [
            item.rejected_input_ids
            for item in items
        ]

        rejected_masks = [
            item.rejected_response_mask
            for item in items
        ]

        chosen_input_ids = self._pad(
            chosen_ids,
            self.pad_token_id,
        )

        rejected_input_ids = self._pad(
            rejected_ids,
            self.pad_token_id,
        )

        chosen_response_mask = self._pad_mask(
            chosen_masks
        )

        rejected_response_mask = self._pad_mask(
            rejected_masks
        )

        chosen_attention_mask = (
            chosen_input_ids
            != self.pad_token_id
        )

        rejected_attention_mask = (
            rejected_input_ids
            != self.pad_token_id
        )

        return PreferenceBatch(
            chosen_input_ids=chosen_input_ids,
            chosen_attention_mask=chosen_attention_mask,
            chosen_response_mask=chosen_response_mask,
            rejected_input_ids=rejected_input_ids,
            rejected_attention_mask=rejected_attention_mask,
            rejected_response_mask=rejected_response_mask,
        )