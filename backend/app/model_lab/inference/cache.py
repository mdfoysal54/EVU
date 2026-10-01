from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class GenerationCache:
    """Request-scoped KV-cache metadata."""

    past_key_values: tuple | None = None

    sequence_length: int = 0

    @property
    def initialized(self) -> bool:
        return self.past_key_values is not None

    def update(
        self,
        past_key_values,
    ) -> None:

        self.past_key_values = (
            past_key_values
        )

        if past_key_values:

            self.sequence_length = int(
                past_key_values[0][0]
                .shape[-2]
            )

        else:

            self.sequence_length = 0

    def reset(self) -> None:

        self.past_key_values = None
        self.sequence_length = 0

    def truncate(
        self,
        keep_tokens: int,
    ) -> None:

        if keep_tokens <= 0:

            self.reset()
            return

        if self.past_key_values is None:
            return

        self.past_key_values = tuple(
            (
                key[
                    :,
                    :,
                    -keep_tokens:,
                    :
                ].contiguous(),

                value[
                    :,
                    :,
                    -keep_tokens:,
                    :
                ].contiguous(),
            )

            for key, value
            in self.past_key_values
        )

        self.sequence_length = min(
            self.sequence_length,
            keep_tokens,
        )


def cache_memory_bytes(
    cache: GenerationCache,
) -> int:

    if cache.past_key_values is None:
        return 0

    return sum(
        key.numel()
        * key.element_size()
        +
        value.numel()
        * value.element_size()

        for key, value
        in cache.past_key_values
    )