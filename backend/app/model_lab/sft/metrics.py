from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SFTMetrics:
    examples: int
    tokens: int
    loss: float
    learning_rate: float
    task_distribution: dict[str, int]

    def to_dict(self) -> dict:
        return {
            "examples": self.examples,
            "tokens": self.tokens,
            "loss": self.loss,
            "learning_rate": self.learning_rate,
            "task_distribution": (
                self.task_distribution
            ),
        }


def task_distribution(
    records: list[dict],
) -> dict[str, int]:
    result: dict[str, int] = {}

    for record in records:
        task_type = str(
            record.get(
                "task_type",
                "general",
            )
        )

        result[task_type] = (
            result.get(task_type, 0)
            + 1
        )

    return result