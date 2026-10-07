from __future__ import annotations

from pathlib import Path

import torch


def lora_state_dict(model) -> dict:
    return {
        name: parameter.detach().cpu()
        for name, parameter in model.named_parameters()
        if "lora_" in name
    }


def save_lora_adapter(
    model,
    path: str | Path,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    torch.save(
        lora_state_dict(model),
        path,
    )

    return path


def load_lora_adapter(
    model,
    path: str | Path,
) -> None:
    state = torch.load(
        path,
        map_location="cpu",
    )

    current = model.state_dict()

    for name, value in state.items():
        if name not in current:
            raise KeyError(
                f"LoRA parameter not found: {name}"
            )

        current[name].copy_(value)