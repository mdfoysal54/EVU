from __future__ import annotations

from collections.abc import Iterable, Iterator


def tokenize_texts(
    texts: Iterable[str],
    tokenizer,
    *,
    add_eos: bool = True,
) -> Iterator[list[int]]:
    eos = tokenizer.eos_token_id

    for text in texts:
        ids = tokenizer.encode(
            text,
            add_special_tokens=False,
        )

        if add_eos:
            ids.append(eos)

        if ids:
            yield ids


def flatten_token_stream(
    sequences: Iterable[list[int]],
) -> Iterator[int]:
    for sequence in sequences:
        yield from sequence