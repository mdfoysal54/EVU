from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

import torch
from torch.utils.data import DataLoader

from app.model_lab.architecture import EVUModelConfig, EVUTransformer
from app.model_lab.tokenizer import ByteBPETokenizer
from app.model_lab.training import (
    CausalBatchCollator,
    CheckpointManager,
    TrainingConfig,
    Trainer,
    create_optimizer,
)
from app.model_lab.experiments.tracker import ExperimentTracker


DEFAULT_TEXTS = [
    "EVU is an independent personal artificial intelligence system.",
    "EVU can operate with its own local model without external AI APIs.",
    "External models are optional specialists used for better quality, lower cost, or difficult tasks.",
    "Memory gives EVU persistent context about projects and conversations.",
    "A language model learns by predicting the next token from previous tokens.",
    "Training quality depends on data quality, tokenizer quality, architecture, optimization, and evaluation.",
    "EVU should measure quality, latency, cost, and reliability before routing a task.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--block-size", type=int, default=128)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output", default="artifacts/evu_tiny")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    tokenizer = ByteBPETokenizer()
    tokenizer.train(DEFAULT_TEXTS)
    tokenizer.save(output / "tokenizer.json")

    config = EVUModelConfig.tiny(vocab_size=len(tokenizer))
    model = EVUTransformer(config)

    sequences = []
    for text in DEFAULT_TEXTS:
        ids = tokenizer.encode(text)
        if len(ids) > args.block_size:
            ids = ids[:args.block_size]
        sequences.append(
            type("Example", (), {"input_ids": ids, "labels": list(ids)})()
        )

    from app.model_lab.training.dataset import LanguageModelDataset
    dataset = LanguageModelDataset(sequences)
    collator = CausalBatchCollator(tokenizer.pad_token_id)
    loader = DataLoader(dataset, batch_size=2, shuffle=True, collate_fn=collator)

    optimizer = create_optimizer(model)
    checkpoints = CheckpointManager(output / "checkpoints")
    trainer = Trainer(
        model,
        optimizer,
        config=TrainingConfig(
            epochs=args.epochs,
            device=args.device,
            log_every=10,
            save_every_steps=max(0, args.steps),
        ),
        checkpoint_manager=checkpoints,
    )

    tracker = ExperimentTracker(output / "experiments")
    run = tracker.start("evu-tiny-smoke", config=config.to_dict())

    result = trainer.fit(loader)
    tracker.log_metrics(run, train_loss=result.average_loss, global_step=result.global_step)

    checkpoints.save(
        name="final.pt",
        model=model,
        optimizer=optimizer,
        epoch=result.epochs_completed,
        global_step=result.global_step,
        extra={"model_config": config.to_dict()},
    )

    print("EVU TINY TRAINING COMPLETE")
    print(result)


if __name__ == "__main__":
    main()