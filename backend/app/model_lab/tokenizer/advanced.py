from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class TokenizationStats:
    documents: int = 0
    tokens: int = 0
    truncated_documents: int = 0
    empty_documents: int = 0


class AdvancedTokenizer:
    """
    Adapter around the existing EVU tokenizer.

    It adds:
    - batch encoding
    - truncation
    - special-token control
    - statistics
    """

    def __init__(self, tokenizer) -> None:
        self.tokenizer = tokenizer

    @property
    def pad_token_id(self) -> int:
        return self.tokenizer.pad_token_id

    @property
    def eos_token_id(self) -> int:
        return self.tokenizer.eos_token_id

    def encode(
        self,
        text: str,
        *,
        max_length: int | None = None,
        add_special_tokens: bool = True,
    ) -> tuple[list[int], bool]:
        ids = self.tokenizer.encode(
            text,
            add_special_tokens=add_special_tokens,
        )

        truncated = False

        if max_length is not None and len(ids) > max_length:
            ids = ids[:max_length]
            truncated = True

        return ids, truncated

    def encode_batch(
        self,
        texts: Iterable[str],
        *,
        max_length: int | None = None,
        add_special_tokens: bool = True,
    ) -> tuple[list[list[int]], TokenizationStats]:
        result: list[list[int]] = []
        stats = TokenizationStats()

        for text in texts:
            stats.documents += 1

            ids, truncated = self.encode(
                text,
                max_length=max_length,
                add_special_tokens=add_special_tokens,
            )

            if not ids:
                stats.empty_documents += 1
                continue

            if truncated:
                stats.truncated_documents += 1

            stats.tokens += len(ids)
            result.append(ids)

        return result, stats

    def decode(self, ids: list[int]) -> str:
        return self.tokenizer.decode(ids)