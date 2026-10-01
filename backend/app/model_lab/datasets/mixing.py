from __future__ import annotations

import random
from typing import Sequence, TypeVar

T = TypeVar("T")


def mix_records(
    datasets: Sequence[Sequence[T]],
    weights: Sequence[float] | None = None,
    seed: int = 42,
) -> list[T]:
    if not datasets:
        return []
    weights = list(weights or [1.0] * len(datasets))
    if len(weights) != len(datasets):
        raise ValueError("weights must match datasets")
    if any(w < 0 for w in weights) or sum(weights) <= 0:
        raise ValueError("weights must be non-negative and not all zero")

    rng = random.Random(seed)
    remaining = [list(items) for items in datasets]
    result: list[T] = []

    while any(remaining):
        available = [i for i, items in enumerate(remaining) if items]
        probs = [weights[i] for i in available]
        total = sum(probs)
        r = rng.random() * total
        chosen = available[-1]
        cumulative = 0.0
        for idx, prob in zip(available, probs):
            cumulative += prob
            if r <= cumulative:
                chosen = idx
                break
        result.append(remaining[chosen].pop(0))
    return result