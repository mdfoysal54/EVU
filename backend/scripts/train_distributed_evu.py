from __future__ import annotations

import argparse

import torch
from torch.utils.data import DataLoader, TensorDataset

from app.model_lab.architecture import (
    EVUModelConfig,
    EVUTransformer,
)
from app.model_lab.distributed import (
    build_distributed_sampler,
    cleanup_distributed,
    setup_distributed,
    wrap_ddp,
)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--strategy",
        choices=("ddp", "fsdp"),
        default="ddp",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--steps",
        type=int,
        default=10,
    )

    return parser.parse_args()


def main():
    args = parse_args()

    runtime = setup_distributed()

    try:
        device = torch.device(
            "cuda",
            runtime.local_rank,
        )

        config = EVUModelConfig.tiny(
            vocab_size=512
        )

        model = EVUTransformer(
            config
        ).to(device)

        if args.strategy == "ddp":
            model = wrap_ddp(
                model,
                local_rank=runtime.local_rank,
            )
        else:
            from app.model_lab.distributed.wrapper import (
                wrap_fsdp,
            )

            model = wrap_fsdp(
                model
            )

        dataset = TensorDataset(
            torch.randint(
                0,
                config.vocab_size,
                (128, 64),
            )
        )

        if runtime.distributed:
            sampler = build_distributed_sampler(
                dataset
            )
        else:
            sampler = None

        loader = DataLoader(
            dataset,
            batch_size=args.batch_size,
            sampler=sampler,
            shuffle=(
                sampler is None
            ),
        )

        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=3e-4,
        )

        model.train()

        step = 0

        for batch in loader:
            input_ids = batch[0].to(
                device
            )

            output = model(
                input_ids,
                labels=input_ids,
            )

            if output.loss is None:
                raise RuntimeError(
                    "Model did not return loss."
                )

            output.loss.backward()

            optimizer.step()
            optimizer.zero_grad(
                set_to_none=True
            )

            step += 1

            if runtime.is_main_process:
                print(
                    f"step={step} "
                    f"loss={output.loss.item():.4f}"
                )

            if step >= args.steps:
                break

    finally:
        cleanup_distributed()


if __name__ == "__main__":
    main()