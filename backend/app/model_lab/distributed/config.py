from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DistributedConfig:
    backend: str = "nccl"
    strategy: str = "ddp"

    rank: int = 0
    local_rank: int = 0
    world_size: int = 1

    gradient_as_bucket_view: bool = True
    find_unused_parameters: bool = False

    mixed_precision: bool = True

    @property
    def distributed(self) -> bool:
        return self.world_size > 1