from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import torch
from torch.utils.data import DataLoader

from .dataset import (
    PreferenceBatch,
    PreferenceCollator,
    PreferenceDataset,
)
from .loss import (
    dpo_loss,
    sequence_log_probability,
)
from .schema import PreferenceExample


@dataclass
class DPOTrainingConfig:
    epochs: int = 1
    batch_size: int = 2

    learning_rate: float = 5e-6
    weight_decay: float = 0.01

    beta: float = 0.1
    label_smoothing: float = 0.0

    max_length: int = 1024

    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0

    validation_fraction: float = 0.05

    device: str = "cpu"
    seed: int = 42


class DPOTrainer:
    """
    Direct Preference Optimization trainer.

    The policy model is trained.

    The reference model remains frozen and represents
    the behavior before preference optimization.
    """

    def __init__(
        self,
        policy_model,
        reference_model,
        tokenizer,
        config: DPOTrainingConfig | None = None,
    ) -> None:
        self.policy_model = policy_model
        self.reference_model = reference_model
        self.tokenizer = tokenizer

        self.config = (
            config
            or DPOTrainingConfig()
        )

        torch.manual_seed(
            self.config.seed
        )

        self.device = torch.device(
            self.config.device
        )

        self.policy_model.to(
            self.device
        )

        self.reference_model.to(
            self.device
        )

        self.reference_model.eval()

        for parameter in (
            self.reference_model.parameters()
        ):
            parameter.requires_grad = False

        self.optimizer = torch.optim.AdamW(
            self.policy_model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
        )

    def _loader(
        self,
        examples: list[PreferenceExample],
        shuffle: bool,
    ) -> DataLoader:
        dataset = PreferenceDataset(
            examples,
            self.tokenizer,
            max_length=self.config.max_length,
        )

        collator = PreferenceCollator(
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

    @staticmethod
    def _move_batch(
        batch: PreferenceBatch,
        device: torch.device,
    ) -> PreferenceBatch:
        return PreferenceBatch(
            chosen_input_ids=batch.chosen_input_ids.to(
                device
            ),
            chosen_attention_mask=batch.chosen_attention_mask.to(
                device
            ),
            chosen_response_mask=batch.chosen_response_mask.to(
                device
            ),
            rejected_input_ids=batch.rejected_input_ids.to(
                device
            ),
            rejected_attention_mask=batch.rejected_attention_mask.to(
                device
            ),
            rejected_response_mask=batch.rejected_response_mask.to(
                device
            ),
        )

    def _model_logps(
        self,
        model,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        response_mask: torch.Tensor,
    ) -> torch.Tensor:
        output = model(
            input_ids,
            attention_mask=attention_mask,
        )

        return sequence_log_probability(
            output.logits,
            input_ids,
            response_mask,
        )

    def _batch_loss(
        self,
        batch: PreferenceBatch,
    ) -> tuple[
        torch.Tensor,
        dict[str, float],
    ]:
        policy_chosen = self._model_logps(
            self.policy_model,
            batch.chosen_input_ids,
            batch.chosen_attention_mask,
            batch.chosen_response_mask,
        )

        policy_rejected = self._model_logps(
            self.policy_model,
            batch.rejected_input_ids,
            batch.rejected_attention_mask,
            batch.rejected_response_mask,
        )

        with torch.no_grad():
            reference_chosen = self._model_logps(
                self.reference_model,
                batch.chosen_input_ids,
                batch.chosen_attention_mask,
                batch.chosen_response_mask,
            )

            reference_rejected = self._model_logps(
                self.reference_model,
                batch.rejected_input_ids,
                batch.rejected_attention_mask,
                batch.rejected_response_mask,
            )

        losses, dpo_logits = dpo_loss(
            policy_chosen,
            policy_rejected,
            reference_chosen,
            reference_rejected,
            beta=self.config.beta,
            label_smoothing=self.config.label_smoothing,
        )

        loss = losses.mean()

        chosen_preference_accuracy = (
            (
                policy_chosen
                > policy_rejected
            )
            .float()
            .mean()
        )

        reference_accuracy = (
            (
                reference_chosen
                > reference_rejected
            )
            .float()
            .mean()
        )

        metrics = {
            "loss": float(
                loss.detach().cpu()
            ),
            "preference_accuracy": float(
                chosen_preference_accuracy.detach().cpu()
            ),
            "reference_accuracy": float(
                reference_accuracy.detach().cpu()
            ),
            "mean_policy_chosen_logp": float(
                policy_chosen.detach().mean().cpu()
            ),
            "mean_policy_rejected_logp": float(
                policy_rejected.detach().mean().cpu()
            ),
            "mean_reference_chosen_logp": float(
                reference_chosen.detach().mean().cpu()
            ),
            "mean_reference_rejected_logp": float(
                reference_rejected.detach().mean().cpu()
            ),
            "mean_dpo_margin": float(
                dpo_logits.detach().mean().cpu()
            ),
        }

        return loss, metrics

    @torch.no_grad()
    def evaluate(
        self,
        examples: list[PreferenceExample],
    ) -> dict[str, Any]:
        self.policy_model.eval()

        loader = self._loader(
            examples,
            shuffle=False,
        )

        total_loss = 0.0
        total_accuracy = 0.0
        batches = 0

        for batch in loader:
            batch = self._move_batch(
                batch,
                self.device,
            )

            loss, metrics = self._batch_loss(
                batch
            )

            total_loss += float(
                loss.detach().cpu()
            )

            total_accuracy += metrics[
                "preference_accuracy"
            ]

            batches += 1

        average_loss = (
            total_loss / max(1, batches)
        )

        try:
            perplexity_like = math.exp(
                min(average_loss, 20.0)
            )
        except OverflowError:
            perplexity_like = float("inf")

        return {
            "loss": average_loss,
            "preference_accuracy": (
                total_accuracy
                / max(1, batches)
            ),
            "examples": len(
                loader.dataset
            ),
            "perplexity_like": perplexity_like,
        }

    def fit(
        self,
        train_examples: list[PreferenceExample],
        validation_examples: list[PreferenceExample] | None = None,
    ) -> dict[str, Any]:
        if not train_examples:
            raise ValueError(
                "DPO training requires at least one example."
            )

        loader = self._loader(
            train_examples,
            shuffle=True,
        )

        if validation_examples:
            validation = validation_examples
        else:
            validation = []

        history: list[dict[str, Any]] = []

        global_step = 0

        for epoch in range(
            self.config.epochs
        ):
            self.policy_model.train()

            self.optimizer.zero_grad(
                set_to_none=True
            )

            running_loss = 0.0
            running_accuracy = 0.0

            for index, batch in enumerate(
                loader
            ):
                batch = self._move_batch(
                    batch,
                    self.device,
                )

                loss, metrics = (
                    self._batch_loss(
                        batch
                    )
                )

                scaled_loss = (
                    loss
                    / self.config.gradient_accumulation_steps
                )

                scaled_loss.backward()

                should_step = (
                    (
                        index + 1
                    )
                    % self.config.gradient_accumulation_steps
                    == 0
                    or index == len(loader) - 1
                )

                if should_step:
                    torch.nn.utils.clip_grad_norm_(
                        self.policy_model.parameters(),
                        self.config.max_grad_norm,
                    )

                    self.optimizer.step()

                    self.optimizer.zero_grad(
                        set_to_none=True
                    )

                    global_step += 1

                running_loss += metrics[
                    "loss"
                ]

                running_accuracy += metrics[
                    "preference_accuracy"
                ]

            train_loss = (
                running_loss
                / max(1, len(loader))
            )

            train_accuracy = (
                running_accuracy
                / max(1, len(loader))
            )

            epoch_result = {
                "epoch": epoch + 1,
                "global_step": global_step,
                "train_loss": train_loss,
                "train_preference_accuracy": train_accuracy,
            }

            if validation:
                validation_result = (
                    self.evaluate(
                        validation
                    )
                )

                epoch_result[
                    "validation"
                ] = validation_result

            history.append(
                epoch_result
            )

        return {
            "epochs": self.config.epochs,
            "global_step": global_step,
            "train_examples": len(
                train_examples
            ),
            "validation_examples": len(
                validation
            ),
            "history": history,
        }