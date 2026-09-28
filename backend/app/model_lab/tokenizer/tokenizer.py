"""
EVU tokenizer.

This is a lightweight baseline tokenizer intended for
development and experimentation.

It can later be replaced by BPE/SentencePiece/Unigram
without changing the training interfaces.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .vocab import Vocabulary


@dataclass
class TokenizerConfig:
    """
    Tokenizer configuration.
    """

    lowercase: bool = False

    add_bos: bool = True

    add_eos: bool = True

    unknown_token: str = "<unk>"

    pad_token: str = "<pad>"

    bos_token: str = "<bos>"

    eos_token: str = "<eos>"


class EVUTokenizer:
    """
    Simple regex-based tokenizer.

    It provides a stable interface for EVU Model Lab.
    """

    def __init__(
        self,
        vocabulary: Vocabulary | None = None,
        config: TokenizerConfig | None = None,
    ) -> None:

        self.config = (
            config
            or TokenizerConfig()
        )

        self.vocabulary = (
            vocabulary
            or Vocabulary()
        )

        self._ensure_special_tokens()

    def _ensure_special_tokens(
        self,
    ) -> None:

        special_tokens = {
            "unk": self.config.unknown_token,
            "pad": self.config.pad_token,
            "bos": self.config.bos_token,
            "eos": self.config.eos_token,
        }

        for name, token in (
            special_tokens.items()
        ):
            self.vocabulary.add_special_token(
                name,
                token,
            )

    def tokenize(
        self,
        text: str,
    ) -> list[str]:

        if self.config.lowercase:
            text = text.lower()

        return re.findall(
            r"\w+|[^\w\s]",
            text,
            flags=re.UNICODE,
        )

    def train(
        self,
        texts: Iterable[str],
    ) -> int:

        tokens = []

        for text in texts:
            tokens.extend(
                self.tokenize(text)
            )

        return self.vocabulary.add_tokens(
            tokens
        )

    def encode(
        self,
        text: str,
        *,
        add_special_tokens: bool = True,
    ) -> list[int]:

        tokens = self.tokenize(text)

        ids = []

        if (
            add_special_tokens
            and self.config.add_bos
        ):
            ids.append(
                self.vocabulary.get_id(
                    self.config.bos_token
                )
            )

        unknown_id = self.vocabulary.get_id(
            self.config.unknown_token
        )

        for token in tokens:
            token_id = (
                self.vocabulary.get_id(
                    token,
                    unknown_id,
                )
            )

            ids.append(token_id)

        if (
            add_special_tokens
            and self.config.add_eos
        ):
            ids.append(
                self.vocabulary.get_id(
                    self.config.eos_token
                )
            )

        return [
            int(token_id)
            for token_id in ids
        ]

    def decode(
        self,
        ids: Iterable[int],
        *,
        skip_special_tokens: bool = True,
    ) -> str:

        special_values = set(
            self.vocabulary.special_tokens.values()
        )

        tokens = []

        for index in ids:
            token = self.vocabulary.get_token(
                int(index),
                self.config.unknown_token,
            )

            if (
                skip_special_tokens
                and token in special_values
            ):
                continue

            tokens.append(token)

        text = " ".join(tokens)

        text = re.sub(
            r"\s+([,.!?;:%])",
            r"\1",
            text,
        )

        return text

    def __len__(self) -> int:
        return len(self.vocabulary)

    @property
    def pad_token_id(self) -> int:
        return int(
            self.vocabulary.get_id(
                self.config.pad_token
            )
        )

    @property
    def unk_token_id(self) -> int:
        return int(
            self.vocabulary.get_id(
                self.config.unknown_token
            )
        )

    @property
    def bos_token_id(self) -> int:
        return int(
            self.vocabulary.get_id(
                self.config.bos_token
            )
        )

    @property
    def eos_token_id(self) -> int:
        return int(
            self.vocabulary.get_id(
                self.config.eos_token
            )
        )