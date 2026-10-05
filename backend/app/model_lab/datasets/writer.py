from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Any


def write_jsonl(
    path: str | Path,
    records: Iterable[Any],
) -> int:

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    count = 0

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:

        for record in records:

            if hasattr(
                record,
                "to_dict",
            ):
                data = record.to_dict()
            else:
                data = record

            handle.write(
                json.dumps(
                    data,
                    ensure_ascii=False,
                )
            )

            handle.write("\n")

            count += 1

    return count