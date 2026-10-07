from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ShardWriter:
    def __init__(
        self,
        output_dir: str | Path,
        *,
        records_per_shard: int = 10_000,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.records_per_shard = max(1, records_per_shard)

    def write(
        self,
        records: list[dict[str, Any]],
        prefix: str,
    ) -> list[Path]:
        paths: list[Path] = []

        for start in range(0, len(records), self.records_per_shard):
            chunk = records[
                start:start + self.records_per_shard
            ]

            shard_index = len(paths)

            path = self.output_dir / (
                f"{prefix}-{shard_index:05d}.jsonl"
            )

            with path.open("w", encoding="utf-8") as handle:
                for record in chunk:
                    handle.write(
                        json.dumps(
                            record,
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

            paths.append(path)

        return paths