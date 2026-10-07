from __future__ import annotations

import json
from pathlib import Path

import torch

from .lora import LoRALinear


def save_lora_adapter(
    model,
    output_dir: str | Path,
) -> Path:
    output = Path(output_dir)
    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    state = {}

    for name, module in model.named_modules():
        if isinstance(module, LoRALinear):
            state[f"{name}.lora_a.weight"] = (
                module.lora_a.weight.detach().cpu()
            )

            state[f"{name}.lora_b.weight"] = (
                module.lora_b.weight.detach().cpu()
            )

    torch.save(
        state,
        output / "adapter.pt",
    )

    metadata = {
        "type": "evu-lora",
        "parameters": len(state),
    }

    (output / "adapter.json").write_text(
        json.dumps(
            metadata,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output / "adapter.pt"


def load_lora_adapter(
    model,
    adapter_path: str | Path,
) -> None:
    state = torch.load(
        adapter_path,
        map_location="cpu",
    )

    for name, module in model.named_modules():
        if not isinstance(module, LoRALinear):
            continue

        a_key = f"{name}.lora_a.weight"
        b_key = f"{name}.lora_b.weight"

        if a_key in state:
            module.lora_a.weight.data.copy_(
                state[a_key]
            )

        if b_key in state:
            module.lora_b.weight.data.copy_(
                state[b_key]
            )