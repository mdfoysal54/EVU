from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
)

import time

import torch

from .engine import (
    EVUInferenceEngine,
    GenerationConfig,
)

from .quantization import (
    parameter_bytes,
    parameter_count,
)


@dataclass
class InferenceBenchmarkResult:

    device: str

    batch_size: int

    prompt_tokens: int

    new_tokens: int

    cached_seconds: float

    uncached_seconds: float

    cached_tokens_per_second: float

    uncached_tokens_per_second: float

    parameter_count: int

    parameter_bytes: int

    def to_dict(self) -> dict:
        return asdict(self)


def _sync(
    device: torch.device,
) -> None:

    if device.type == "cuda":
        torch.cuda.synchronize(
            device
        )


@torch.no_grad()
def benchmark_generation(
    model,
    input_ids: torch.Tensor,
    *,
    new_tokens: int = 32,
) -> InferenceBenchmarkResult:

    device = next(
        model.parameters()
    ).device

    engine = EVUInferenceEngine(
        model,
        tokenizer=None,
        device=str(device),
    )

    cached_config = (
        GenerationConfig(
            max_new_tokens=new_tokens,
            greedy=True,
            use_cache=True,
        )
    )

    uncached_config = (
        GenerationConfig(
            max_new_tokens=new_tokens,
            greedy=True,
            use_cache=False,
        )
    )

    _sync(device)

    start = time.perf_counter()

    engine.generate_ids(
        input_ids,
        cached_config,
    )

    _sync(device)

    cached = (
        time.perf_counter()
        - start
    )

    _sync(device)

    start = time.perf_counter()

    engine.generate_ids(
        input_ids,
        uncached_config,
    )

    _sync(device)

    uncached = (
        time.perf_counter()
        - start
    )

    batch_size = int(
        input_ids.shape[0]
    )

    cached_tps = (
        new_tokens
        * batch_size
    ) / max(
        cached,
        1e-9,
    )

    uncached_tps = (
        new_tokens
        * batch_size
    ) / max(
        uncached,
        1e-9,
    )

    return InferenceBenchmarkResult(
        device=str(device),
        batch_size=batch_size,
        prompt_tokens=int(
            input_ids.shape[1]
        ),
        new_tokens=new_tokens,
        cached_seconds=cached,
        uncached_seconds=uncached,
        cached_tokens_per_second=cached_tps,
        uncached_tokens_per_second=uncached_tps,
        parameter_count=parameter_count(
            model
        ),
        parameter_bytes=parameter_bytes(
            model
        ),
    )