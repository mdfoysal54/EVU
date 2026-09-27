import json
import random
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset

from app.research.modeling.checkpoint import (
    save_checkpoint,
)
from app.research.modeling.config import (
    EVUModelConfig,
)
from app.research.modeling.transformer import (
    EVUTransformerLM,
)


class EVUTokenDataset(Dataset):

    def __init__(
        self,
        sequences: list[list[int]],
        max_length: int,
    ):
        self.sequences = sequences
        self.max_length = max_length

    def __len__(self):
        return len(
            self.sequences
        )

    def __getitem__(
        self,
        index: int,
    ):

        sequence = self.sequences[
            index
        ]

        if len(sequence) > self.max_length:
            sequence = sequence[
                : self.max_length
            ]

        if len(sequence) < 2:
            sequence = (
                sequence
                + [0, 2]
            )

        input_ids = sequence[
            :-1
        ]

        labels = sequence[
            1:
        ]

        input_ids = (
            input_ids
            + [0]
            * (
                self.max_length
                - 1
                - len(input_ids)
            )
        )

        labels = (
            labels
            + [-100]
            * (
                self.max_length
                - 1
                - len(labels)
            )
        )

        return {
            "input_ids": torch.tensor(
                input_ids,
                dtype=torch.long,
            ),
            "labels": torch.tensor(
                labels,
                dtype=torch.long,
            ),
        }


def load_sequences(
    path: str,
) -> list[list[int]]:

    source = Path(path)

    with source.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def get_model_config(
    model_size: str,
) -> EVUModelConfig:

    normalized = (
        model_size.lower()
    )

    if normalized == "tiny":
        return EVUModelConfig.tiny()

    if normalized == "small":
        return EVUModelConfig.small()

    if normalized == "evu-100m":
        return EVUModelConfig.evu_100m()

    if normalized == "evu-300m":
        # Placeholder scaling configuration.
        return EVUModelConfig(
            vocab_size=32768,
            max_sequence_length=2048,
            hidden_size=1024,
            num_layers=24,
            num_attention_heads=16,
            intermediate_size=4096,
            dropout=0.1,
        )

    if normalized == "evu-1b":
        return EVUModelConfig(
            vocab_size=32768,
            max_sequence_length=4096,
            hidden_size=2048,
            num_layers=24,
            num_attention_heads=16,
            intermediate_size=8192,
            dropout=0.1,
        )

    raise ValueError(
        f"Unknown model size: {model_size}"
    )


def train_model(
    dataset_dir: str,
    output_dir: str,
    model_size: str = "tiny",
    epochs: int = 1,
    batch_size: int = 2,
    learning_rate: float = 3e-4,
    max_sequence_length: int = 256,
    seed: int = 42,
    device: str | None = None,
) -> dict:

    random.seed(seed)
    torch.manual_seed(seed)

    if device is None:

        device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

    dataset_path = (
        Path(dataset_dir)
        / "train.json"
    )

    sequences = load_sequences(
        str(dataset_path)
    )

    if not sequences:
        raise ValueError(
            "Training dataset is empty."
        )

    config = get_model_config(
        model_size
    )

    # Ensure training does not accidentally
    # exceed the model's configured context.
    max_sequence_length = min(
        max_sequence_length,
        config.max_sequence_length,
    )

    dataset = EVUTokenDataset(
        sequences,
        max_sequence_length,
    )

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
    )

    model = EVUTransformerLM(
        config
    ).to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=0.1,
    )

    output = Path(
        output_dir
    )

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.train()

    global_step = 0
    final_loss = None

    for epoch in range(epochs):

        for batch in loader:

            input_ids = (
                batch["input_ids"]
                .to(device)
            )

            labels = (
                batch["labels"]
                .to(device)
            )

            optimizer.zero_grad()

            result = model(
                input_ids,
                labels=labels,
            )

            loss = result["loss"]

            if loss is None:
                continue

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=1.0,
            )

            optimizer.step()

            global_step += 1

            final_loss = float(
                loss.item()
            )

        checkpoint_path = (
            output
            / f"checkpoint-epoch-{epoch + 1}.pt"
        )

        save_checkpoint(
            model=model,
            optimizer=optimizer,
            epoch=epoch + 1,
            step=global_step,
            loss=final_loss
            if final_loss is not None
            else 0.0,
            path=str(
                checkpoint_path
            ),
        )

    return {
        "status": "completed",
        "device": device,
        "model_size": model_size,
        "epochs": epochs,
        "steps": global_step,
        "final_loss": final_loss,
        "checkpoint_dir": str(
            output
        ),
    }