from __future__ import annotations

import os

import torch.distributed as dist

from .config import DistributedConfig
from .environment import (
    DistributedEnvironment,
    read_environment,
)


def initialize_process_group(
    config: DistributedConfig,
) -> DistributedEnvironment:
    environment = read_environment()

    os.environ.setdefault(
        "MASTER_ADDR",
        config.master_addr,
    )

    os.environ.setdefault(
        "MASTER_PORT",
        str(config.master_port),
    )

    if environment.world_size <= 1:
        return environment

    if not dist.is_initialized():
        dist.init_process_group(
            backend=config.backend,
            rank=environment.rank,
            world_size=environment.world_size,
        )

    return environment


def cleanup_process_group() -> None:
    if dist.is_available() and dist.is_initialized():
        dist.destroy_process_group()