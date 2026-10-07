from __future__ import annotations

import os
from dataclasses import dataclass

import torch
import torch.distributed as dist


@dataclass
class DistributedRuntime:
    rank: int
    local_rank: int
    world_size: int

    @property
    def is_main_process(self) -> bool:
        return self.rank == 0

    @property
    def distributed(self) -> bool:
        return self.world_size > 1


def setup_distributed(
    backend: str | None = None,
) -> DistributedRuntime:
    world_size = int(
        os.environ.get(
            "WORLD_SIZE",
            "1",
        )
    )

    rank = int(
        os.environ.get(
            "RANK",
            "0",
        )
    )

    local_rank = int(
        os.environ.get(
            "LOCAL_RANK",
            "0",
        )
    )

    if world_size <= 1:
        return DistributedRuntime(
            rank=0,
            local_rank=0,
            world_size=1,
        )

    if not torch.cuda.is_available():
        raise RuntimeError(
            "Multi-process CUDA training requires CUDA."
        )

    torch.cuda.set_device(
        local_rank
    )

    selected_backend = backend or "nccl"

    if not dist.is_initialized():
        dist.init_process_group(
            backend=selected_backend,
            rank=rank,
            world_size=world_size,
        )

    return DistributedRuntime(
        rank=rank,
        local_rank=local_rank,
        world_size=world_size,
    )


def cleanup_distributed() -> None:
    if dist.is_available() and dist.is_initialized():
        dist.destroy_process_group()