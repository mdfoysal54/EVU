from __future__ import annotations

from torch import nn

from .config import LoRAConfig
from .layer import LoRALinear


def _replace_child(
    parent: nn.Module,
    name: str,
    module: nn.Module,
) -> None:
    setattr(parent, name, module)


def inject_lora(
    model: nn.Module,
    config: LoRAConfig,
) -> nn.Module:
    for parameter in model.parameters():
        parameter.requires_grad = False

    targets = set(config.target_modules)

    for parent_name, parent in model.named_modules():
        for child_name, child in list(
            parent.named_children()
        ):
            if child_name not in targets:
                continue

            if not isinstance(child, nn.Linear):
                continue

            _replace_child(
                parent,
                child_name,
                LoRALinear(
                    child,
                    rank=config.rank,
                    alpha=config.alpha,
                    dropout=config.dropout,
                ),
            )

    return model


def trainable_parameters(
    model: nn.Module,
) -> tuple[int, int]:
    trainable = 0
    total = 0

    for parameter in model.parameters():
        total += parameter.numel()

        if parameter.requires_grad:
            trainable += parameter.numel()

    return trainable, total