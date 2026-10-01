from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from app.model_lab.architecture.config import (
    EVUModelConfig,
)

from app.model_lab.tokenizer.byte_bpe import (
    ByteBPETokenizer,
)


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Prepare a deployable EVU "
            "owned-model bundle."
        )
    )

    parser.add_argument(
        "--checkpoint",
        required=True,
    )

    parser.add_argument(
        "--tokenizer",
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

    checkpoint = torch.load(
        args.checkpoint,
        map_location="cpu",
        weights_only=False,
    )

    state_dict = checkpoint.get(
        "model_state_dict",
        checkpoint,
    )

    torch.save(
        {
            "model_state_dict": state_dict,
        },
        output / "model.pt",
    )

    tokenizer = (
        ByteBPETokenizer.load(
            args.tokenizer
        )
    )

    tokenizer.save(
        output / "tokenizer.json"
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
        f"EVU model bundle created at: {output}"
    )


if __name__ == "__main__":
    main()