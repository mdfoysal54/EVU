from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add backend directory to sys.path so 'app' can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.model_lab.datasets import (
    build_specialized_datasets,
    write_jsonl,
)

from app.model_lab.experience import (
    ExperienceStore,
)


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Build EVU reasoning, coding "
            "and tool-use datasets."
        )
    )

    parser.add_argument(
        "--input",
        default=(
            "./data/experience/runtime.jsonl"
        ),
    )

    parser.add_argument(
        "--output",
        default=(
            "./data/specialized"
        ),
    )

    parser.add_argument(
        "--minimum-score",
        type=float,
        default=0.75,
    )

    args = parser.parse_args()

    store = ExperienceStore(
        args.input
    )

    experiences = store.load_all()

    result = build_specialized_datasets(
        experiences,
        minimum_score=args.minimum_score,
    )

    output = Path(
        args.output
    )
    output.mkdir(parents=True, exist_ok=True)

    reasoning_count = write_jsonl(
        output / "reasoning.jsonl",
        result.reasoning,
    )

    coding_count = write_jsonl(
        output / "coding.jsonl",
        result.coding,
    )

    tool_count = write_jsonl(
        output / "tool_use.jsonl",
        result.tool_use,
    )

    summary = {
        "input_experiences":
            len(experiences),
        "reasoning":
            reasoning_count,
        "coding":
            coding_count,
        "tool_use":
            tool_count,
        "total":
            reasoning_count
            + coding_count
            + tool_count,
    }

    (output / "summary.json").write_text(
        json.dumps(
            summary,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()