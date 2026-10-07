from __future__ import annotations

from collections.abc import Iterable, Iterator

from .schema import PackedSequence


def pack_token_stream(
    sequences: Iterable[list[int]],
    block_size: int,
    *,
    drop_remainder: bool = True,
) -> Iterator[PackedSequence]:
    if block_size <= 1:
        raise ValueError("block_size must be > 1")

    buffer: list[int] = []

    for sequence in sequences:
        buffer.extend(sequence)

        while len(buffer) >= block_size:
            chunk = buffer[:block_size]
            del buffer[:block_size]

            yield PackedSequence(
                input_ids=chunk,
                labels=chunk.copy(),
            )

    if buffer and not drop_remainder:
        yield PackedSequence(
            input_ids=buffer,
            labels=buffer.copy(),
        )