"""
Tokenizer training utilities.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .tokenizer import EVUTokenizer


@dataclass
class TokenizerTrainingConfig:
    """
    Controls vocabulary construction.
    """

    min_frequency: int = 1

    max_vocabulary_size: int | None = None


class TokenizerTrainer:
    """
    Builds a tokenizer vocabulary from text.
    """

    def __init__(
        self,
        tokenizer: EVUTokenizer,
        config: TokenizerTrainingConfig | None = None,
    ) -> None:

        self.tokenizer = tokenizer

        self.config = (
            config
            or TokenizerTrainingConfig()
        )

    def train(
        self,
        texts: Iterable[str],
    ) -> EVUTokenizer:

        counter = Counter()

        for text in texts:
            counter.update(
                self.tokenizer.tokenize(text)
            )

        candidates = [
            token
            for token, frequency
            in counter.most_common()
            if frequency
            >= self.config.min_frequency
        ]

        if (
            self.config.max_vocabulary_size
            is not None
        ):
            reserved = len(
                self.tokenizer.vocabulary
            )

            remaining = max(
                0,
                self.config.max_vocabulary_size
                - reserved,
            )

            candidates = candidates[
                :remaining
            ]

        self.tokenizer.vocabulary.add_tokens(
            candidates
        )

        return self.tokenizer