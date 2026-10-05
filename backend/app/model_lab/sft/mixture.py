from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class MixtureConfig:
    reasoning_weight: float = 1.0
    coding_weight: float = 1.0
    tool_use_weight: float = 1.0
    seed: int = 42


def mix_specialized(
    reasoning: list[dict],
    coding: list[dict],
    tool_use: list[dict],
    config: MixtureConfig | None = None,
) -> list[dict]:
    config = config or MixtureConfig()

    sources = [
        ("reasoning", reasoning, config.reasoning_weight),
        ("coding", coding, config.coding_weight),
        ("tool_use", tool_use, config.tool_use_weight),
    ]

    rng = random.Random(
        config.seed
    )

    result: list[dict] = []

    for task_type, records, weight in sources:
        if weight <= 0:
            continue

        for record in records:
            item = dict(record)

            item["task_type"] = (
                task_type
            )

            item["_mixture_weight"] = (
                weight
            )

            result.append(item)

    rng.shuffle(result)

    return result