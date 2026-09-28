"""
Dataset utilities for EVU Model Lab.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

try:
    import torch  # type: ignore[import-not-found]
    from torch.utils.data import Dataset  # type: ignore[import-not-found]
except ImportError:
    torch = None

    class Dataset:
        pass


@dataclass
class TokenSequence:
    """
    A tokenized training example.
    """

    input_ids: list[int]

    labels: list[int] | None = None

    metadata: dict | None = None


class LanguageModelDataset(Dataset):
    """
    Dataset for causal language-model training.
    """

    def __init__(
        self,
        sequences: Sequence[
            TokenSequence
        ],
    ) -> None:

        self.sequences = list(
            sequences
        )

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(
        self,
        index: int,
    ) -> TokenSequence:

        return self.sequences[index]


class TextDataset(LanguageModelDataset):
    """
    Builds token sequences from raw text.
    """

    def __init__(
        self,
        texts: Iterable[str],
        tokenizer,
        *,
        max_length: int | None = None,
    ) -> None:

        sequences = []

        for text in texts:

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
                )
            )

        super().__init__(sequences)