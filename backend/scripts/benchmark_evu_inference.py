from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from app.model_lab.architecture.config import (
    EVUModelConfig,
)

from app.model_lab.architecture.model import (
    EVUTransformer,
)

from app.model_lab.inference.benchmark import (
    benchmark_generation,
)


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Benchmark EVU "
            "KV-cache inference"
        )
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
        "--prompt-tokens",
        type=int,
        default=32,
    )

    parser.add_argument(
        "--new-tokens",
        type=int,
        default=32,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
    )

    parser.add_argument(
        "--device",
        default="cpu",
    )

    parser.add_argument(
        "--output",
        default="",
    )

    args = parser.parse_args()

    config = EVUModelConfig(
        **json.loads(
            Path(
                args.config
            ).read_text(
                encoding="utf-8"
            )
        )
    )

    model = EVUTransformer(
        config
    )

    checkpoint = torch.load(
        args.checkpoint,
        map_location=args.device,
        weights_only=False,
    )

    state = checkpoint.get(
        "model_state_dict",
        checkpoint,
    )

    model.load_state_dict(
        state
    )

    model.to(
        args.device
    ).eval()

    input_ids = torch.randint(
        0,
        config.vocab_size,
        (
            args.batch_size,
            args.prompt_tokens,
        ),
        dtype=torch.long,
        device=args.device,
    )

    result = benchmark_generation(
        model,
        input_ids,
        new_tokens=args.new_tokens,
    )

    payload = result.to_dict()

    print(
        json.dumps(
            payload,
            indent=2,
        )
    )

    if args.output:

        output_path = Path(
            args.output
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json.dumps(
                payload,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()