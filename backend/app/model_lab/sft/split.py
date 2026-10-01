from __future__ import annotations

import random
from typing import Sequence, TypeVar


T = TypeVar("T")


def split_examples(
    examples: Sequence[T],
    *,
    validation_fraction: float = 0.05,
    seed: int = 42,
) -> tuple[list[T], list[T]]:

    if not 0.0 < validation_fraction < 1.0:
        raise ValueError(
            "validation_fraction must be greater than 0 "
            "and less than 1."
        )

    items = list(examples)

    if len(items) < 2:
        raise ValueError(
            "At least two examples are required."
        )

    rng = random.Random(seed)
    rng.shuffle(items)

    validation_size = max(
        1,
        int(round(
            len(items)
            * validation_fraction
        )),
    )

    validation_size = min(
        validation_size,
        len(items) - 1,
    )

    validation = items[
        :validation_size
    ]

    training = items[
        validation_size:
    ]

    return training, validation