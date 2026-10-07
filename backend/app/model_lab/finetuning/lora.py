from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass
class LoRAConfig:
    rank: int = 8
    alpha: float = 16.0
    dropout: float = 0.05
    bias: str = "none"

    @property
    def scaling(self) -> float:
        return self.alpha / self.rank


class LoRALinear(nn.Module):
    """
    Linear layer with a frozen base projection plus LoRA adapters.

    y = W(x) + scale * B(A(x))
    """

    def __init__(
        self,
        base: nn.Linear,
        config: LoRAConfig,
    ) -> None:
        super().__init__()

        self.base = base
        self.config = config

        for parameter in self.base.parameters():
            parameter.requires_grad = False

        self.lora_a = nn.Linear(
            base.in_features,
            config.rank,
            bias=False,
        )

        self.lora_b = nn.Linear(
            config.rank,
            base.out_features,
            bias=False,
        )

        self.dropout = nn.Dropout(
            config.dropout
        )

        nn.init.kaiming_uniform_(
            self.lora_a.weight,
            a=5**0.5,
        )

        nn.init.zeros_(
            self.lora_b.weight
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        base_output = self.base(x)

        adapter = self.lora_b(
            self.lora_a(
                self.dropout(x)
            )
        )

        return base_output + (
            adapter * self.config.scaling
        )

    def merged(self) -> nn.Linear:
        """
        Returns a normal Linear containing the LoRA update.
        """

        merged = nn.Linear(
            self.base.in_features,
            self.base.out_features,
            bias=self.base.bias is not None,
        ).to(
            device=self.base.weight.device,
            dtype=self.base.weight.dtype,
        )

        with torch.no_grad():
            update = (
                self.lora_b.weight
                @ self.lora_a.weight
            ) * self.config.scaling

            merged.weight.copy_(
                self.base.weight + update
            )

            if (
                self.base.bias is not None
                and merged.bias is not None
            ):
                merged.bias.copy_(
                    self.base.bias
                )

        return merged


def _replace_child(
    parent: nn.Module,
    name: str,
    replacement: nn.Module,
) -> None:
    setattr(
        parent,
        name,
        replacement,
    )


def inject_lora(
    model: nn.Module,
    config: LoRAConfig | None = None,
    *,
    target_modules: tuple[str, ...] = (
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ),
) -> nn.Module:
    config = config or LoRAConfig()

    for parameter in model.parameters():
        parameter.requires_grad = False

    for module_name, module in list(
        model.named_modules()
    ):
        if not isinstance(module, nn.Linear):
            continue

        short_name = module_name.rsplit(
            ".",
            1,
        )[-1]

        if short_name not in target_modules:
            continue

        if "." in module_name:
            parent_name, child_name = module_name.rsplit(
                ".",
                1,
            )

            parent = model.get_submodule(
                parent_name
            )
        else:
            parent = model
            child_name = module_name

        replacement = LoRALinear(
            module,
            config,
        )

        _replace_child(
            parent,
            child_name,
            replacement,
        )

    return model


def lora_parameters(
    model: nn.Module,
):
    for module in model.modules():
        if isinstance(module, LoRALinear):
            yield module.lora_a.weight
            yield module.lora_b.weight


def trainable_parameter_count(
    model: nn.Module,
) -> int:
    return sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )