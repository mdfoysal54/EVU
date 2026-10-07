from __future__ import annotations

import torch
from torch import nn


def wrap_ddp(
    model: nn.Module,
    *,
    local_rank: int,
    find_unused_parameters: bool = False,
) -> nn.Module:
    if not torch.cuda.is_available():
        raise RuntimeError(
            "DDP CUDA wrapper requires CUDA."
        )

    from torch.nn.parallel import DistributedDataParallel

    return DistributedDataParallel(
        model,
        device_ids=[local_rank],
        output_device=local_rank,
        find_unused_parameters=find_unused_parameters,
        gradient_as_bucket_view=True,
    )


def wrap_fsdp(
    model: nn.Module,
) -> nn.Module:
    if not torch.cuda.is_available():
        raise RuntimeError(
            "FSDP requires CUDA for this EVU implementation."
        )

    try:
        from torch.distributed.fsdp import (
            FullyShardedDataParallel,
        )
    except ImportError as exc:
        raise RuntimeError(
            "This PyTorch installation does not provide FSDP."
        ) from exc

    return FullyShardedDataParallel(
        model
    )