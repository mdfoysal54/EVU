from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


@dataclass
class Splitter:
    validation_ratio: float = 0.02
    seed: int = 42

    def __post_init__(self) -> None:
        if not 0.0 < self.validation_ratio < 1.0:
            raise ValueError("validation_ratio must be between 0 and 1")

    def split(self, records: list[T]) -> tuple[list[T], list[T]]:
        items = list(records)

        rng = random.Random(self.seed)
        rng.shuffle(items)

        validation_count = max(
            1,
            int(len(items) * self.validation_ratio),
        ) if len(items) > 1 else 0

        if validation_count == 0:
            return items, []

        validation = items[:validation_count]
        train = items[validation_count:]

        return train, validation