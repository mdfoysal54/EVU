from __future__ import annotations

import argparse
from pathlib import Path

import torch

from app.model_lab.architecture import (
    EVUModelConfig,
    EVUTransformer,
)
from app.model_lab.finetuning.adapter_io import (
    save_lora_adapter,
)
from app.model_lab.finetuning.efficient import (
    EfficientTrainer,
    EfficientTrainingConfig,
)
from app.model_lab.finetuning.lora import (
    LoRAConfig,
    inject_lora,
    trainable_parameter_count,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

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
        "--device",
        default="cpu",
    )

    parser.add_argument(
        "--rank",
        type=int,
        default=8,
    )

    parser.add_argument(
        "--alpha",
        type=float,
        default=16,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config_data = torch.load(
        args.config,
        map_location="cpu",
    ) if args.config.endswith(".pt") else None

    if config_data is None:
        import json

        config_data = json.loads(
            Path(args.config).read_text(
                encoding="utf-8"
            )
        )

    config = EVUModelConfig(
        **config_data
    )

    model = EVUTransformer(config)

    checkpoint = torch.load(
        args.checkpoint,
        map_location="cpu",
    )

    state_dict = checkpoint.get(
        "model",
        checkpoint,
    )

    model.load_state_dict(
        state_dict,
        strict=False,
    )

    model = inject_lora(
        model,
        LoRAConfig(
            rank=args.rank,
            alpha=args.alpha,
        ),
    )

    device = torch.device(
        args.device
    )

    model.to(device)

    optimizer = torch.optim.AdamW(
        [
            parameter
            for parameter in model.parameters()
            if parameter.requires_grad
        ],
        lr=2e-4,
    )

    trainer = EfficientTrainer(
        model,
        optimizer,
        config=EfficientTrainingConfig(
            gradient_accumulation_steps=1,
            use_amp=(
                device.type == "cuda"
            ),
        ),
        device=device,
    )

    print(
        "trainable_parameters:",
        trainable_parameter_count(model),
    )

    print(
        "LoRA model ready.",
        "Connect the existing EVU SFT/DPO dataloader",
        "to trainer.train_batch(...) for training.",
    )

    output = Path(args.output)
    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_lora_adapter(
        model,
        output,
    )


if __name__ == "__main__":
    main()