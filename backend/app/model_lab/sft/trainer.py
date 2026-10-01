from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch.utils.data import DataLoader

from .dataset import (
    SFTCollator,
    SFTDataset,
)
from .schema import ConversationExample
from .split import split_examples


@dataclass
class SFTTrainingConfig:

    epochs: int = 1

    batch_size: int = 2

    learning_rate: float = 2e-5

    weight_decay: float = 0.01

    validation_fraction: float = 0.05

    max_length: int = 1024

    gradient_accumulation_steps: int = 1

    max_grad_norm: float = 1.0

    device: str = "cpu"

    seed: int = 42


@dataclass
class SFTValidationResult:

    loss: float

    perplexity: float

    examples: int


class SFTTrainer:

    def __init__(
        self,
        model,
        tokenizer,
        config: SFTTrainingConfig | None = None,
    ) -> None:

        self.model = model

        self.tokenizer = tokenizer

        self.config = (
            config
            or SFTTrainingConfig()
        )

        torch.manual_seed(
            self.config.seed
        )

        if (
            self.config.device.startswith("cuda")
            and not torch.cuda.is_available()
        ):
            raise RuntimeError(
                "CUDA was requested but is not available."
            )

        self.device = torch.device(
            self.config.device
        )

        self.model.to(self.device)

        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
        )

    def _build_loader(
        self,
        examples: list[
            ConversationExample
        ],
        *,
        shuffle: bool,
    ):

        dataset = SFTDataset(
            examples,
            self.tokenizer,
            max_length=self.config.max_length,
        )

        collator = SFTCollator(
            pad_token_id=getattr(
                self.tokenizer,
                "pad_token_id",
                0,
            )
        )

        return DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=shuffle,
            collate_fn=collator,
        )

    def _forward_loss(
        self,
        batch,
    ) -> torch.Tensor:

        input_ids = (
            batch.input_ids.to(
                self.device
            )
        )

        labels = (
            batch.labels.to(
                self.device
            )
        )

        attention_mask = (
            batch.attention_mask.to(
                self.device
            )
        )

        output = self.model(
            input_ids=input_ids,
            labels=labels,
            attention_mask=attention_mask,
        )

        loss = output.get("loss")

        if loss is None:
            raise RuntimeError(
                "EVU model did not return a loss."
            )

        return loss

    @torch.no_grad()
    def validate(
        self,
        examples: list[
            ConversationExample
        ],
    ) -> SFTValidationResult:

        self.model.eval()

        loader = self._build_loader(
            examples,
            shuffle=False,
        )

        total_loss = 0.0
        batches = 0

        for batch in loader:

            loss = self._forward_loss(
                batch
            )

            total_loss += float(
                loss.detach().cpu()
            )

            batches += 1

        average_loss = (
            total_loss
            / max(1, batches)
        )

        try:
            perplexity = math.exp(
                min(average_loss, 20.0)
            )
        except OverflowError:
            perplexity = float("inf")

        return SFTValidationResult(
            loss=average_loss,
            perplexity=perplexity,
            examples=len(loader.dataset),
        )

    def fit(
        self,
        examples: list[
            ConversationExample
        ],
    ) -> dict:

        if not examples:
            raise ValueError(
                "No SFT examples supplied."
            )

        (
            train_examples,
            validation_examples,
        ) = split_examples(
            examples,
            validation_fraction=(
                self.config.validation_fraction
            ),
            seed=self.config.seed,
        )

        train_loader = self._build_loader(
            train_examples,
            shuffle=True,
        )

        global_step = 0

        history = []

        for epoch in range(
            self.config.epochs
        ):

            self.model.train()

            self.optimizer.zero_grad(
                set_to_none=True
            )

            running_loss = 0.0

            for batch_index, batch in enumerate(
                train_loader
            ):

                loss = self._forward_loss(
                    batch
                )

                scaled_loss = (
                    loss
                    / self.config
                    .gradient_accumulation_steps
                )

                scaled_loss.backward()

                should_update = (
                    (
                        batch_index + 1
                    )
                    % self.config
                    .gradient_accumulation_steps
                    == 0
                    or batch_index
                    == len(train_loader) - 1
                )

                if should_update:

                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(),
                        self.config.max_grad_norm,
                    )

                    self.optimizer.step()

                    self.optimizer.zero_grad(
                        set_to_none=True
                    )

                    global_step += 1

                running_loss += float(
                    loss.detach().cpu()
                )

            train_loss = (
                running_loss
                / max(
                    1,
                    len(train_loader),
                )
            )

            validation = self.validate(
                validation_examples
            )

            history.append(
                {
                    "epoch": epoch + 1,
                    "global_step": global_step,
                    "train_loss": train_loss,
                    "validation_loss": validation.loss,
                    "validation_perplexity": (
                        validation.perplexity
                    ),
                }
            )

        return {
            "epochs": self.config.epochs,
            "global_step": global_step,
            "train_examples": len(
                train_examples
            ),
            "validation_examples": len(
                validation_examples
            ),
            "history": history,
        }