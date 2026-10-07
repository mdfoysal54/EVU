import torch
from torch import nn

from app.model_lab.finetuning.lora import (
    LoRAConfig,
    LoRALinear,
    inject_lora,
    trainable_parameter_count,
)


class TinyModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.q_proj = nn.Linear(
            16,
            16,
        )

        self.other = nn.Linear(
            16,
            16,
        )

    def forward(self, x):
        return self.other(
            self.q_proj(x)
        )


def test_lora_forward():
    base = nn.Linear(
        8,
        8,
    )

    layer = LoRALinear(
        base,
        LoRAConfig(
            rank=2,
        ),
    )

    x = torch.randn(
        2,
        8,
    )

    output = layer(x)

    assert output.shape == (
        2,
        8,
    )


def test_lora_injection():
    model = TinyModel()

    inject_lora(
        model,
        LoRAConfig(rank=2),
        target_modules=("q_proj",),
    )

    assert isinstance(
        model.q_proj,
        LoRALinear,
    )

    assert trainable_parameter_count(
        model
    ) > 0


def test_lora_merge():
    base = nn.Linear(
        4,
        4,
    )

    layer = LoRALinear(
        base,
        LoRAConfig(rank=2),
    )

    merged = layer.merged()

    x = torch.randn(
        3,
        4,
    )

    assert torch.allclose(
        layer(x),
        merged(x),
        atol=1e-5,
    )