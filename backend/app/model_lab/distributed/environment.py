from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class DistributedEnvironment:
    rank: int
    local_rank: int
    world_size: int


def read_environment() -> DistributedEnvironment:
    return DistributedEnvironment(
        rank=int(os.environ.get("RANK", "0")),
        local_rank=int(
            os.environ.get(
                "LOCAL_RANK",
                "0",
            )
        ),
        world_size=int(
            os.environ.get(
                "WORLD_SIZE",
                "1",
            )
        ),
    )