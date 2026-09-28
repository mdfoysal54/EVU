"""
Supervised Fine-Tuning utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..tokenizer import EVUTokenizer
from ..training.dataset import (
    TokenSequence,
    LanguageModelDataset,
)


@dataclass
class SFTExample:
    """
    Instruction/response example.
    """

    instruction: str

    response: str

    system: str | None = None


class SFTDataset(
    LanguageModelDataset
):
    """
    Dataset for supervised instruction tuning.
    """

    def __init__(
        self,
        examples: Iterable[SFTExample],
        tokenizer: EVUTokenizer,
        *,
        max_length: int | None = None,
    ) -> None:

        sequences = []

        for example in examples:

            parts = []

            if example.system:
                parts.append(
                    "System: "
                    + example.system
                )

            parts.append(
                "User: "
                + example.instruction
            )

            parts.append(
                "Assistant: "
                + example.response
            )

            text = "\n".join(parts)

            token_ids = tokenizer.encode(
                text
            )

            if max_length is not None:
                token_ids = token_ids[
                    :max_length
                ]

            sequences.append(
                TokenSequence(
                    input_ids=token_ids,
                    labels=list(token_ids),
                    metadata={
                        "type": "sft",
                    },
                )
            )

        super().__init__(
            sequences
        )