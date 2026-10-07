from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.model_lab.registry.artifacts import (
    sha256_file,
)
from app.model_lab.registry.manifest import (
    ModelManifest,
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
        "--artifact",
        required=True,
    )

    parser.add_argument(
        "--dataset-version",
        required=True,
    )

    parser.add_argument(
        "--benchmark-score",
        required=True,
        type=float,
    )

    parser.add_argument(
        "--safety-score",
        required=True,
        type=float,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    artifact = Path(
        args.artifact
    )

    checksum = sha256_file(
        artifact
    )

    manifest = ModelManifest.create(
        model_id=args.model_id,
        version=args.version,
        artifact_path=str(
            artifact
        ),
        checksum=checksum,
        dataset_version=(
            args.dataset_version
        ),
        benchmark_score=(
            args.benchmark_score
        ),
        safety_score=(
            args.safety_score
        ),
    )

    manifest.save(
        args.output
    )

    print(
        json.dumps(
            {
                "model_id": (
                    manifest.model_id
                ),
                "version": (
                    manifest.version
                ),
                "checksum": (
                    manifest.checksum
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()