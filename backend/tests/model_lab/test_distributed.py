import torch

from app.model_lab.distributed.config import (
    DistributedConfig,
)
from app.model_lab.distributed.runtime import (
    DistributedRuntime,
)


def test_distributed_config():
    config = DistributedConfig(
        world_size=4,
    )

    assert config.distributed is True


def test_single_process_runtime():
    runtime = DistributedRuntime(
        rank=0,
        local_rank=0,
        world_size=1,
    )

    assert runtime.is_main_process
    assert not runtime.distributed


def test_cuda_requirement_is_detectable():
    if not torch.cuda.is_available():
        assert torch.cuda.is_available() is False