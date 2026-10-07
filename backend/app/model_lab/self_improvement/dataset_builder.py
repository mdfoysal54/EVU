from __future__ import annotations

import json
from pathlib import Path

from .schema import (
    ImprovementCandidate,
)


def build_sft_dataset(
    examples: list[
        ImprovementCandidate
    ],
    output: str | Path,
) -> None:
    output = Path(output)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for example in examples:
            record = {
                "prompt": example.prompt,
                "response": example.response,
                "task_type": (
                    example.task_type
                ),
                "metadata": {
                    **example.metadata,
                    "source": (
                        "evu_self_improvement"
                    ),
                    "example_id": (
                        example.example_id
                    ),
                },
            }

            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )