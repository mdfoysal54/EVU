from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class QLoRAConfig:
    compute_dtype: str = "float16"
    quantization_dtype: str = "int8"


def prepare_qlora_model(
    model,
    *,
    device: str = "cuda",
    compute_dtype: torch.dtype = torch.float16,
):
    """
    Lightweight QLoRA preparation.

    This intentionally does not pretend to implement
    bitsandbytes 4-bit quantization itself.

    It prepares the model for low-memory adapter training
    and leaves actual 4-bit loading to the optional backend.
    """

    if device.startswith("cuda") and torch.cuda.is_available():
        model = model.to(device=device)

    model = model.to(dtype=compute_dtype)

    for parameter in model.parameters():
        parameter.requires_grad = False

    return model