from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class DatasetSource:
    name: str
    records: list[dict]
    weight: float = 1.0


class DatasetMixer:
    def __init__(self, *, seed: int = 42) -> None:
        self.seed = seed

    def mix(
        self,
        sources: list[DatasetSource],
        *,
        total_records: int | None = None,
    ) -> list[dict]:
        if not sources:
            return []

        rng = random.Random(self.seed)

        if total_records is None:
            total_records = sum(
                len(source.records)
                for source in sources
            )

        weights = [
            max(0.0, source.weight)
            for source in sources
        ]

        total_weight = sum(weights)

        if total_weight <= 0:
            raise ValueError("At least one source must have weight > 0")

        result: list[dict] = []

        pools = [
            list(source.records)
            for source in sources
        ]

        for pool in pools:
            rng.shuffle(pool)

        cursors = [0] * len(pools)

        for _ in range(total_records):
            index = rng.choices(
                range(len(sources)),
                weights=weights,
                k=1,
            )[0]

            pool = pools[index]

            if not pool:
                continue

            cursor = cursors[index]

            result.append(pool[cursor % len(pool)])
            cursors[index] += 1

        rng.shuffle(result)

        return result