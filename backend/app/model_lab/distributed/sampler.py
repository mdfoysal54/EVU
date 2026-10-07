from __future__ import annotations

from torch.utils.data import (
    Dataset,
    DistributedSampler,
)


def build_distributed_sampler(
    dataset: Dataset,
    *,
    shuffle: bool = True,
    seed: int = 42,
):
    return DistributedSampler(
        dataset,
        shuffle=shuffle,
        seed=seed,
    )