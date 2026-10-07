from __future__ import annotations

import argparse
import json

from app.model_lab.registry.active import (
    ActiveModelPointer,
)
from app.model_lab.registry.promotion import (
    decide_promotion,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model-id",
        required=True,
    )

    parser.add_argument(
        "--version",
        required=True,
    )

    parser.add_argument(
        "--from-status",
        default="staging",
    )

    parser.add_argument(
        "--to-status",
        default="production",
    )

    parser.add_argument(
        "--benchmark-score",
        required=True,
        type=float,
    )

    parser.add_argument(
        "--pass-rate",
        required=True,
        type=float,
    )

    parser.add_argument(
        "--safety-score",
        required=True,
        type=float,
    )

    parser.add_argument(
        "--regression",
        default=0.0,
        type=float,
    )

    parser.add_argument(
        "--pointer",
        required=True,
    )

    args = parser.parse_args()

    decision = decide_promotion(
        source_status=args.from_status,
        target_status=args.to_status,
        benchmark_score=(
            args.benchmark_score
        ),
        pass_rate=args.pass_rate,
        safety_score=args.safety_score,
        regression=args.regression,
    )

    if not decision.approved:
        print(
            json.dumps(
                decision.to_dict(),
                indent=2,
            )
        )

        raise SystemExit(
            "MODEL PROMOTION REJECTED"
        )

    pointer = ActiveModelPointer(
        args.pointer
    )

    pointer.set(
        args.model_id,
        args.version,
    )

    print(
        json.dumps(
            {
                "promoted": True,
                "model_id": (
                    args.model_id
                ),
                "version": args.version,
                "status": args.to_status,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()