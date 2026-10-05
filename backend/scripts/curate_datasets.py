from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.model_lab.datasets.curation import (
    curate,
)


def load_jsonl(
    path: Path,
) -> list[dict]:
    records = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            line = line.strip()

            if line:
                records.append(
                    json.loads(line)
                )

    return records


def write_jsonl(
    path: Path,
    records: list[dict],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for record in records:
            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--rejected-output",
        default="",
    )

    args = parser.parse_args()

    result = curate(
        load_jsonl(
            Path(args.input)
        )
    )

    write_jsonl(
        Path(args.output),
        result.accepted,
    )

    if args.rejected_output:
        write_jsonl(
            Path(args.rejected_output),
            result.rejected,
        )

    print(
        json.dumps(
            result.statistics,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()