import torch
from torch import nn

from app.model_lab.finetuning.efficient import (
    EfficientTrainer,
    EfficientTrainingConfig,
)


class TinyLM(nn.Module):
    class Output:
        def __init__(self, loss):
            self.loss = loss

    def __init__(self):
        super().__init__()

        self.linear = nn.Linear(
            8,
            8,
        )

    def forward(
        self,
        input_ids,
        labels=None,
        attention_mask=None,
    ):
        logits = self.linear(
            torch.nn.functional.one_hot(
                input_ids,
                num_classes=8,
            ).float()
        )

        loss = None

        if labels is not None:
            loss = torch.nn.functional.cross_entropy(
                logits.reshape(-1, 8),
                labels.reshape(-1),
            )

        return self.Output(loss)


def test_efficient_trainer():
    model = TinyLM()

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=1e-3,
    )

    trainer = EfficientTrainer(
        model,
        optimizer,
        config=EfficientTrainingConfig(
            gradient_accumulation_steps=2,
            use_amp=False,
        ),
    )

    ids = torch.randint(
        0,
        8,
        (2, 4),
    )

    loss = trainer.train_batch(
        ids,
        ids,
    )

    assert loss > 0
    assert trainer.global_step == 1