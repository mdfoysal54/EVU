from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.model_lab.experience import (
    ExperienceEvaluator,
    ExperiencePipeline,
    ExperienceStore,
)


def write_jsonl(
    path: Path,
    records,
) -> int:

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

            handle.write(
                json.dumps(
                    record.to_dict(),
                    ensure_ascii=False,
                )
            )

            handle.write("\n")

            count += 1

    return count


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Build EVU training datasets "
            "from experience trajectories."
        )
    )

    parser.add_argument(
        "--input",
        default="./data/experience/experiences.jsonl",
    )

    parser.add_argument(
        "--output",
        default="./data/generated",
    )

    parser.add_argument(
        "--minimum-score",
        type=float,
        default=0.70,
    )

    args = parser.parse_args()

    store = ExperienceStore(
        args.input
    )

    evaluator = ExperienceEvaluator(
        minimum_overall=args.minimum_score
    )

    pipeline = ExperiencePipeline(
        store=store,
        evaluator=evaluator,
    )

    result = pipeline.build_datasets(
        minimum_score=args.minimum_score
    )

    output = Path(args.output)

    sft_path = output / "sft.jsonl"
    preference_path = (
        output / "preference.jsonl"
    )
    trajectory_path = (
        output / "trajectory.jsonl"
    )

    sft_count = write_jsonl(
        sft_path,
        result.sft_examples,
    )

    preference_count = write_jsonl(
        preference_path,
        result.preference_examples,
    )

    trajectory_count = write_jsonl(
        trajectory_path,
        result.trajectory_examples,
    )

    summary = {
        "total_experiences":
            result.total_experiences,
        "accepted_experiences":
            result.accepted_experiences,
        "rejected_experiences":
            result.rejected_experiences,
        "sft_examples":
            sft_count,
        "preference_examples":
            preference_count,
        "trajectory_examples":
            trajectory_count,
    }

    summary_path = output / "summary.json"

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False,
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