from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PackingStats:
    source_tokens: int = 0
    packed_tokens: int = 0
    sequences: int = 0

    @property
    def utilization(self) -> float:
        if self.source_tokens == 0:
            return 0.0

        return self.packed_tokens / self.source_tokens