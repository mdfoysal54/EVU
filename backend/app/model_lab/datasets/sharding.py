from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def write_jsonl_shards(records: Iterable[dict], output_dir: str | Path, shard_size: int = 10000) -> list[Path]:
    if shard_size <= 0:
        raise ValueError("shard_size must be positive")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    handle = None
    count = 0
    shard_index = -1

    try:
        for record in records:
            if count % shard_size == 0:
                if handle is not None:
                    handle.close()
                shard_index += 1
                path = output / f"part-{shard_index:05d}.jsonl"
                paths.append(path)
                handle = path.open("w", encoding="utf-8")
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    finally:
        if handle is not None:
            handle.close()
    return paths