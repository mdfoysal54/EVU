from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import torch
from torch.utils.data import Dataset

from .schema import ConversationExample


@dataclass
class EncodedSFTExample:
    input_ids: list[int]
    labels: list[int]
    metadata: dict


class SFTDataset(
    Dataset[EncodedSFTExample]
):
    """
    Supervised fine-tuning dataset.

    Prompt tokens are assigned -100 so PyTorch's cross entropy
    ignores them.

    Assistant tokens remain trainable.
    """

    def __init__(
        self,
        examples: Sequence[ConversationExample],
        tokenizer,
        *,
        max_length: int = 1024,
    ) -> None:

        if max_length < 2:
            raise ValueError(
                "max_length must be at least 2."
            )

        self.items: list[
            EncodedSFTExample
        ] = []

        for example in examples:

            encoded = self._encode_example(
                example,
                tokenizer,
                max_length,
            )

            if encoded is not None:
                self.items.append(encoded)

        if not self.items:
            raise ValueError(
                "SFT dataset contains no usable examples."
            )

    @staticmethod
    def _render_prompt(
        messages,
    ) -> str:

        parts: list[str] = []

        for message in messages[:-1]:

            role = message.role.capitalize()

            parts.append(
                f"{role}: {message.content}"
            )

        parts.append("Assistant:")

        return "\n".join(parts) + " "

    @classmethod
    def _encode_example(
        cls,
        example: ConversationExample,
        tokenizer,
        max_length: int,
    ) -> EncodedSFTExample | None:

        assistant_message = (
            example.messages[-1]
        )

        prompt_text = cls._render_prompt(
            example.messages
        )

        response_text = (
            assistant_message.content
        )

        prompt_ids = tokenizer.encode(
            prompt_text,
            add_special_tokens=True,
        )

        response_ids = tokenizer.encode(
            response_text,
            add_special_tokens=False,
        )

        eos_token_id = getattr(
            tokenizer,
            "eos_token_id",
            None,
        )

        if eos_token_id is not None:
            response_ids = [
                *response_ids,
                int(eos_token_id),
            ]

        input_ids = (
            prompt_ids
            + response_ids
        )

        labels = (
            [-100] * len(prompt_ids)
            + response_ids
        )

        if len(input_ids) > max_length:

            response_budget = min(
                len(response_ids),
                max_length,
            )

            prompt_budget = (
                max_length
                - response_budget
            )

            if prompt_budget > 0:
                prompt_ids = prompt_ids[
                    -prompt_budget:
                ]
            else:
                prompt_ids = []

            response_ids = response_ids[
                :response_budget
            ]

            input_ids = (
                prompt_ids
                + response_ids
            )

            labels = (
                [-100] * len(prompt_ids)
                + response_ids
            )

        if len(input_ids) < 2:
            return None

        return EncodedSFTExample(
            input_ids=input_ids,
            labels=labels,
            metadata=example.metadata or {},
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(
        self,
        index: int,
    ) -> EncodedSFTExample:

        return self.items[index]


@dataclass
class SFTBatch:
    input_ids: torch.Tensor
    labels: torch.Tensor
    attention_mask: torch.Tensor


class SFTCollator:
    def __init__(
        self,
        pad_token_id: int = 0,
    ) -> None:

        self.pad_token_id = int(
            pad_token_id
        )

    def __call__(
        self,
        items: Sequence[
            EncodedSFTExample
        ],
    ) -> SFTBatch:

        if not items:
            raise ValueError(
                "Cannot collate an empty batch."
            )

        max_length = max(
            len(item.input_ids)
            for item in items
        )

        input_ids = []
        labels = []
        attention_masks = []

        for item in items:

            padding = (
                max_length
                - len(item.input_ids)
            )

            input_ids.append(
                item.input_ids
                + [self.pad_token_id]
                * padding
            )

            labels.append(
                item.labels
                + [-100] * padding
            )

            attention_masks.append(
                [1] * len(item.input_ids)
                + [0] * padding
            )

        return SFTBatch(
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