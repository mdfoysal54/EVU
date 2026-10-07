from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass
class QLoRAConfig:
    load_in_4bit: bool = True
    compute_dtype: str = "bfloat16"
    quant_type: str = "nf4"
    double_quant: bool = True


def bitsandbytes_available() -> bool:
    try:
        import bitsandbytes  # noqa: F401
        return True
    except ImportError:
        return False


def require_qlora_backend() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError(
            "QLoRA 4-bit training requires a CUDA-capable "
            "environment for this implementation."
        )

    if not bitsandbytes_available():
        raise RuntimeError(
            "QLoRA requires bitsandbytes. "
            "Install a CUDA-compatible bitsandbytes build."
        )


def quantize_linear_4bit(
    module: nn.Linear,
    config: QLoRAConfig | None = None,
) -> nn.Module:
    """
    Convert a Linear module to bitsandbytes Linear4bit.

    This function deliberately refuses to silently emulate 4-bit
    quantization with float tensors.
    """

    config = config or QLoRAConfig()

    require_qlora_backend()

    import bitsandbytes as bnb

    if config.compute_dtype == "bfloat16":
        compute_dtype = torch.bfloat16
    elif config.compute_dtype == "float16":
        compute_dtype = torch.float16
    else:
        compute_dtype = torch.float32

    replacement = bnb.nn.Linear4bit(
        module.in_features,
        module.out_features,
        bias=module.bias is not None,
        compute_dtype=compute_dtype,
        compress_statistics=config.double_quant,
        quant_type=config.quant_type,
    )

    replacement.load_state_dict(
        module.state_dict()
    )

    return replacement


def prepare_model_for_qlora(
    model: nn.Module,
    *,
    config: QLoRAConfig | None = None,
) -> nn.Module:
    config = config or QLoRAConfig()

    if not config.load_in_4bit:
        return model

    require_qlora_backend()

    for name, module in list(
        model.named_modules()
    ):
        if not isinstance(module, nn.Linear):
            continue

        if "." in name:
            parent_name, child_name = name.rsplit(
                ".",
                1,
            )
            parent = model.get_submodule(
                parent_name
            )
        else:
            parent = model
            child_name = name

        replacement = quantize_linear_4bit(
            module,
            config,
        )

        setattr(
            parent,
            child_name,
            replacement,
        )

    for parameter in model.parameters():
        parameter.requires_grad = False

    return model