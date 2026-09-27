import argparse
import json

from app.research.pipeline.prepare import (
    prepare_dataset,
)

from app.research.training.trainer import (
    train_model,
)


def main():

    parser = argparse.ArgumentParser(
        description="EVU Research Training"
    )

    parser.add_argument(
        "--dataset",
        required=True,
        help="Input JSONL dataset",
    )

    parser.add_argument(
        "--prepared-dir",
        default="./research_output/prepared",
    )

    parser.add_argument(
        "--output-dir",
        default="./research_output/models",
    )

    parser.add_argument(
        "--model-size",
        default="tiny",
        choices=[
            "tiny",
            "small",
            "evu-100m",
            "evu-300m",
            "evu-1b",
        ],
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=1,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=3e-4,
    )

    parser.add_argument(
        "--max-sequence-length",
        type=int,
        default=256,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    args = parser.parse_args()

    print(
        "\n=== EVU DATA PREPARATION ===\n"
    )

    statistics = prepare_dataset(
        input_path=args.dataset,
        output_dir=args.prepared_dir,
    )

    print(
        json.dumps(
            statistics,
            indent=2,
        )
    )

    print(
        "\n=== EVU MODEL TRAINING ===\n"
    )

    result = train_model(
        dataset_dir=args.prepared_dir,
        output_dir=args.output_dir,
        model_size=args.model_size,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        max_sequence_length=(
            args.max_sequence_length
        ),
        seed=args.seed,
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()