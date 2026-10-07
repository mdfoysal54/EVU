from __future__ import annotations

import json
from pathlib import Path

from .schema import BenchmarkCase


def load_jsonl(
    path: str | Path,
) -> list[BenchmarkCase]:
    path = Path(path)

    cases: list[BenchmarkCase] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            1,
        ):
            line = line.strip()

            if not line:
                continue

            record = json.loads(line)

            case_id = str(
                record.get(
                    "id",
                    f"{path.stem}:{line_number}",
                )
            )

            category = str(
                record.get(
                    "category",
                    "general",
                )
            )

            prompt = str(
                record.get(
                    "prompt",
                    record.get(
                        "instruction",
                        "",
                    ),
                )
            )

            cases.append(
                BenchmarkCase(
                    case_id=case_id,
                    category=category,
                    prompt=prompt,
                    expected=record.get(
                        "expected"
                    ),
                    metadata=dict(
                        record.get(
                            "metadata",
                            {},
                        )
                    ),
                )
            )

    return cases