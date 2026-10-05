from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.model_lab.evaluation.dataset_eval import (
    evaluate_records,
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

            if not line:
                continue

            records.append(
                json.loads(line)
            )

    return records


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
    )

    parser.add_argument(
        "--output",
        default="dataset_evaluation.json",
    )

    args = parser.parse_args()

    records = load_jsonl(
        Path(args.input)
    )

    result = evaluate_records(
        records
    )

    output = {
        "total": result.total,
        "accepted": result.accepted,
        "rejected": result.rejected,
        "average_score": result.average_score,
        "acceptance_rate": (
            result.acceptance_rate
        ),
        "rejection_reasons": (
            result.rejection_reasons
        ),
    }

    Path(args.output).write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            output,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()