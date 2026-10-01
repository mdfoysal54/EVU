from __future__ import annotations

import copy

import torch


def parameter_count(model) -> int:
    return sum(
        p.numel()
        for p in model.parameters()
    )


def parameter_bytes(model) -> int:
    return sum(
        p.numel() * p.element_size()
        for p in model.parameters()
    )


def memory_bytes(
    model,
    dtype_bytes: int = 4,
) -> int:
    """Compatibility helper for uniform dtype estimation."""

    return (
        parameter_count(model)
        * dtype_bytes
    )


def cast_model(
    model,
    dtype: torch.dtype,
):
    return model.to(
        dtype=dtype
    )


def prepare_inference_dtype(
    model,
    device: str | torch.device,
):
    """Prepare CUDA model for lower-precision inference.

    CPU stays float32.

    CUDA:
      BF16 if supported
      otherwise FP16
    """

    device_obj = torch.device(
        device
    )

    if device_obj.type != "cuda":
        return model

    if torch.cuda.is_bf16_supported():
        return model.to(
            dtype=torch.bfloat16
        )

    return model.to(
        dtype=torch.float16
    )


def quantize_dynamic_int8(model):
    """Create a CPU dynamic-INT8 model."""

    if torch.cuda.is_available() and any(
        p.is_cuda
        for p in model.parameters()
    ):
        raise ValueError(
            "Move the model to CPU before "
            "dynamic int8 quantization"
        )

    try:

        from torch.ao.quantization import (
            quantize_dynamic,
        )

    except ImportError as exc:

        raise RuntimeError(
            "This PyTorch build does not "
            "provide torch.ao.quantization"
        ) from exc

    model_cpu = (
        copy.deepcopy(model)
        .cpu()
        .eval()
    )

    return quantize_dynamic(
        model_cpu,
        {torch.nn.Linear},
        dtype=torch.qint8,
    )