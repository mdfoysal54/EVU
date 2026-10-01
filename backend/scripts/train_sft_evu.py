from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from app.model_lab.architecture.config import (
    EVUModelConfig,
)

from app.model_lab.architecture.model import (
    EVUForCausalLM,
)

from app.model_lab.sft.schema import (
    load_jsonl_examples,
)

from app.model_lab.sft.trainer import (
    SFTTrainer,
    SFTTrainingConfig,
)

from app.model_lab.tokenizer.byte_bpe import (
    ByteBPETokenizer,
)


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Supervised fine-tune an EVU "
            "owned-model checkpoint."
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
        default=2e-5,
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

    return parser.parse_args()


def main():

    args = parse_args()

    output = Path(
        args.output
    )

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    tokenizer = (
        ByteBPETokenizer.load(
            args.tokenizer
        )
    )

    config_data = json.loads(
        Path(
            args.config
        ).read_text(
            encoding="utf-8"
        )
    )

    config = EVUModelConfig(
        **config_data
    )

    model = EVUForCausalLM(
        config
    )

    checkpoint = torch.load(
        args.checkpoint,
        map_location=args.device,
        weights_only=False,
    )

    state_dict = checkpoint.get(
        "model_state_dict",
        checkpoint,
    )

    model.load_state_dict(
        state_dict
    )

    examples = load_jsonl_examples(
        args.dataset
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        config=SFTTrainingConfig(
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr,
            max_length=args.max_length,
            device=args.device,
        ),
    )

    result = trainer.fit(
        examples
    )

    torch.save(
        {
            "model_state_dict": (
                model.state_dict()
            ),
            "sft_result": result,
            "base_checkpoint": (
                str(args.checkpoint)
            ),
        },
        output / "model.pt",
    )

    (
        output
        / "training_result.json"
    ).write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    tokenizer.save(
        output / "tokenizer.json"
    )

    (
        output
        / "config.json"
    ).write_text(
        json.dumps(
            config.to_dict(),
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


if __name__ == "__main__":
    main()