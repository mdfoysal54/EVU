from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.model_lab.benchmark.datasets import (
    load_jsonl,
)
from app.model_lab.benchmark.runner import (
    BenchmarkRunner,
)
from app.model_lab.benchmark.report import (
    build_report,
    save_report,
)
from app.model_lab.benchmark.scorers import (
    exact_match,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        required=True,
    )

    parser.add_argument(
        "--model-id",
        required=True,
    )

    parser.add_argument(
        "--version",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    cases = load_jsonl(
        Path(args.dataset)
    )

    raise SystemExit(
        "Connect the --generator argument "
        "to EVU's local model serving layer. "
        "This script intentionally does not "
        "call an external model API."
    )


if __name__ == "__main__":
    main()