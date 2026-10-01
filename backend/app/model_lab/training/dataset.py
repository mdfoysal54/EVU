from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

try:
    import torch
    from torch.utils.data import Dataset
except ImportError:  # pragma: no cover
    torch = None
    class Dataset:
        pass


@dataclass
class TokenSequence:
    input_ids: list[int]
    labels: list[int] | None = None
    metadata: dict | None = None


class LanguageModelDataset(Dataset):
    def __init__(self, sequences: Sequence[TokenSequence]) -> None:
        self.sequences = list(sequences)

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, index: int) -> TokenSequence:
        return self.sequences[index]


class TextDataset(LanguageModelDataset):
    def __init__(
        self,
        texts: Iterable[str],
        tokenizer,
        *,
        max_length: int | None = None,
    ) -> None:
        sequences = []
        for text in texts:
            token_ids = tokenizer.encode(text)
            if max_length is not None:
                token_ids = token_ids[:max_length]
            if len(token_ids) >= 2:
                sequences.append(TokenSequence(input_ids=token_ids, labels=list(token_ids)))
        super().__init__(sequences)


def make_packed_dataset(
    texts: Iterable[str],
    tokenizer,
    block_size: int,
) -> LanguageModelDataset:
    from ..preprocessing.pack import pack_tokens
    sequences = [tokenizer.encode(text) for text in texts]
    packed = pack_tokens(sequences, block_size, getattr(tokenizer, "eos_token_id", None))
    return LanguageModelDataset(
        [TokenSequence(input_ids=seq, labels=list(seq)) for seq in packed]
    )