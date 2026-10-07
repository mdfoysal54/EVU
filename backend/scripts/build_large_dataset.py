from __future__ import annotations

import argparse

from app.model_lab.datasets.large_scale import (
    Deduplicator,
    LargeScaleDatasetPipeline,
    QualityFilter,
    Splitter,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an EVU large-scale training dataset."
    )

    parser.add_argument(
        "--input",
        nargs="+",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--name",
        default="evu-pretraining",
    )

    parser.add_argument(
        "--version",
        default="v1",
    )

    parser.add_argument(
        "--text-field",
        default="text",
    )

    parser.add_argument(
        "--validation-ratio",
        type=float,
        default=0.02,
    )

    parser.add_argument(
        "--records-per-shard",
        type=int,
        default=10000,
    )

    parser.add_argument(
        "--min-chars",
        type=int,
        default=50,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pipeline = LargeScaleDatasetPipeline(
        quality_filter=QualityFilter(
            min_chars=args.min_chars,
        ),
        deduplicator=Deduplicator(),
        splitter=Splitter(
            validation_ratio=args.validation_ratio,
        ),
    )

    manifest = pipeline.process(
        args.input,
        args.output,
        dataset_name=args.name,
        dataset_version=args.version,
        text_field=args.text_field,
        records_per_shard=args.records_per_shard,
    )

    print("EVU LARGE DATASET BUILD COMPLETE")
    print(manifest.to_dict())
    print("manifest_sha256:", manifest.checksum())


if __name__ == "__main__":
    main()