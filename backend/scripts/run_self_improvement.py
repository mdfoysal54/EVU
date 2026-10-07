from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.model_lab.self_improvement.collector import (
    load_experiences,
)
from app.model_lab.self_improvement.loop import (
    SelfImprovementLoop,
)
from app.model_lab.self_improvement.schema import (
    ImprovementConfig,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--experiences",
        required=True,
    )

    parser.add_argument(
        "--output-dataset",
        required=True,
    )

    parser.add_argument(
        "--min-examples",
        type=int,
        default=20,
    )

    args = parser.parse_args()

    config = ImprovementConfig(
        min_examples=args.min_examples
    )

    loop = SelfImprovementLoop(
        config
    )

    records = load_experiences(
        args.experiences
    )

    selected = (
        loop.collect_and_select(
            records
        )
    )

    if not selected:
        print(
            "No high-quality experiences "
            "available for self-improvement."
        )
        return

    if len(selected) < (
        config.min_examples
    ):
        print(
            json.dumps(
                {
                    "selected": len(
                        selected
                    ),
                    "required": (
                        config.min_examples
                    ),
                    "status": (
                        "waiting_for_more_data"
                    ),
                },
                indent=2,
            )
        )

        return

    output = loop.build_dataset(
        selected,
        args.output_dataset,
    )

    print(
        json.dumps(
            {
                "selected": len(selected),
                "dataset": output,
                "status": "ready_for_training",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()