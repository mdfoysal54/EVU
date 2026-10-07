from __future__ import annotations

import torch


class LoRATrainer:
    def __init__(
        self,
        model,
        learning_rate: float = 2e-4,
    ) -> None:
        self.model = model

        parameters = [
            parameter
            for parameter in model.parameters()
            if parameter.requires_grad
        ]

        if not parameters:
            raise ValueError(
                "No trainable LoRA parameters found"
            )

        self.optimizer = torch.optim.AdamW(
            parameters,
            lr=learning_rate,
        )

    def train_step(
        self,
        input_ids,
        labels,
        attention_mask=None,
    ) -> float:
        self.model.train()

        self.optimizer.zero_grad(
            set_to_none=True
        )

        output = self.model(
            input_ids,
            attention_mask=attention_mask,
            labels=labels,
        )

        if output.loss is None:
            raise RuntimeError(
                "Model did not return loss"
            )

        output.loss.backward()

        self.optimizer.step()

        return float(
            output.loss.detach().cpu()
        )