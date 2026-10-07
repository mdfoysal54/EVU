from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TokenizationConfig:
    block_size: int = 1024
    add_eos: bool = True
    drop_remainder: bool = True


@dataclass
class PackedSequence:
    input_ids: list[int]
    labels: list[int]

    @property
    def length(self) -> int:
        return len(self.input_ids)