from __future__ import annotations

from collections.abc import Iterable


def pack_tokens(sequences: Iterable[list[int]], block_size: int, eos_token_id: int | None = None) -> list[list[int]]:
    if block_size <= 1:
        raise ValueError("block_size must be > 1")
    stream: list[int] = []
    for seq in sequences:
        stream.extend(seq)
        if eos_token_id is not None and (not stream or stream[-1] != eos_token_id):
            stream.append(eos_token_id)
    return [stream[i : i + block_size] for i in range(0, len(stream) - block_size + 1, block_size)]