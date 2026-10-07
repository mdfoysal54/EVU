from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LoRAConfig:
    rank: int = 8
    alpha: float = 16.0
    dropout: float = 0.05

    target_modules: tuple[str, ...] = (
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    )

    bias: str = "none"

    def scaling(self) -> float:
        return self.alpha / self.rank