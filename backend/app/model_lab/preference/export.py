from __future__ import annotations

import json
from pathlib import Path

from .pairs import PreferencePair


def write_preference_jsonl(
    pairs: list[PreferencePair],
    path: str | Path,
) -> None:
    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for pair in pairs:
            handle.write(
                json.dumps(
                    pair.to_dict(),
                    ensure_ascii=False,
                )
                + "\n"
            )