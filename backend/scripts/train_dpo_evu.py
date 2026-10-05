from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import torch

from app.model_lab.architecture.config import (
    EVUModelConfig,
)
from app.model_lab.architecture.model import (
    EVUTransformer,
)
from app.model_lab.preference.schema import (
    load_preference_jsonl,
)
from app.model_lab.preference.trainer import (
    DPOTrainer,
    DPOTrainingConfig,
)
from app.model_lab.tokenizer.byte_bpe import (
    ByteBPETokenizer,
)


def load_model(
    checkpoint_path: str,
    config_path: str,
    device: str,
) -> EVUTransformer:
    config_payload = json.loads(
        Path(config_path).read_text(
            encoding="utf-8"
        )
    )

    config = EVUModelConfig(
        **config_payload
    )

    model = EVUTransformer(config)

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )

    state = checkpoint.get(
        "model_state_dict",
        checkpoint,
    )

    model.load_state_dict(
        state
    )

    return model


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Preference-align an EVU checkpoint "
            "using Direct Preference Optimization."
        )
    )

    parser.add_argument(
        "--dataset",
        required=True,
    )

    parser.add_argument(
        "--tokenizer",
        required=True,
    )

    parser.add_argument(
        "--checkpoint",
        required=True,
        help="SFT or other policy checkpoint.",
    )

    parser.add_argument(
        "--config",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
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
        "--lr",
        type=float,
        default=5e-6,
    )

    parser.add_argument(
        "--beta",
        type=float,
        default=0.1,
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=1024,
    )

    parser.add_argument(
        "--device",
        default="cpu",
    )

    args = parser.parse_args()

    output = Path(
        args.output
    )

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Loading tokenizer..."
    )

    tokenizer = ByteBPETokenizer.load(
        args.tokenizer
    )

    print(
        "Loading policy model..."
    )

    policy_model = load_model(
        args.checkpoint,
        args.config,
        args.device,
    )

    print(
        "Creating frozen reference model..."
    )

    reference_model = copy.deepcopy(
        policy_model
    )

    for parameter in (
        reference_model.parameters()
    ):
        parameter.requires_grad = False

    examples = load_preference_jsonl(
        args.dataset
    )

    if len(examples) < 2:
        raise ValueError(
            "DPO training requires at least "
            "two preference examples."
        )

    # Keep a simple deterministic split.
    split_index = max(
        1,
        int(len(examples) * 0.9),
    )

    if split_index >= len(examples):
        split_index = len(examples) - 1

    train_examples = examples[
        :split_index
    ]

    validation_examples = examples[
        split_index:
    ]

    print(
        f"Preference examples: {len(examples)}"
    )

    print(
        f"Training examples: {len(train_examples)}"
    )

    print(
        f"Validation examples: "
        f"{len(validation_examples)}"
    )

    trainer = DPOTrainer(
        policy_model=policy_model,
        reference_model=reference_model,
        tokenizer=tokenizer,
        config=DPOTrainingConfig(
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr,
            beta=args.beta,
            max_length=args.max_length,
            device=args.device,
        ),
    )

    result = trainer.fit(
        train_examples,
        validation_examples,
    )

    torch.save(
        {
            "model_state_dict": (
                policy_model.state_dict()
            ),
            "dpo_result": result,
            "base_checkpoint": str(
                args.checkpoint
            ),
            "algorithm": "DPO",
            "beta": args.beta,
        },
        output / "model.pt",
    )

    tokenizer.save(
        output / "tokenizer.json"
    )

    config = EVUModelConfig(
        **json.loads(
            Path(args.config).read_text(
                encoding="utf-8"
            )
        )
    )

    (
        output / "config.json"
    ).write_text(
        json.dumps(
            config.to_dict(),
            indent=2,
        ),
        encoding="utf-8",
    )

    (
        output / "training_result.json"
    ).write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    print(
        f"\nDPO model saved to: {output}"
    )


if __name__ == "__main__":
    main()