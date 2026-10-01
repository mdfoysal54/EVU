from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class EVUModelConfig:
    """Configuration for EVU's decoder-only causal language model."""

    vocab_size: int = 4096
    hidden_size: int = 256
    num_layers: int = 6
    num_attention_heads: int = 8
    num_key_value_heads: int | None = None
    intermediate_size: int | None = None
    max_position_embeddings: int = 1024
    rope_theta: float = 10000.0
    dropout: float = 0.0
    rms_norm_eps: float = 1e-6
    attention_bias: bool = False
    mlp_bias: bool = False
    tie_word_embeddings: bool = True
    initializer_range: float = 0.02
    pad_token_id: int = 0
    bos_token_id: int = 1
    eos_token_id: int = 2
    use_cache: bool = True

    def __post_init__(self) -> None:
        if self.vocab_size < 8:
            raise ValueError("vocab_size must be >= 8")
        if self.hidden_size <= 0:
            raise ValueError("hidden_size must be positive")
        if self.num_layers <= 0:
            raise ValueError("num_layers must be positive")
        if self.num_attention_heads <= 0:
            raise ValueError("num_attention_heads must be positive")
        if self.hidden_size % self.num_attention_heads:
            raise ValueError("hidden_size must be divisible by num_attention_heads")

        if self.num_key_value_heads is None:
            self.num_key_value_heads = self.num_attention_heads

        if self.num_attention_heads % self.num_key_value_heads:
            raise ValueError("num_attention_heads must be divisible by num_key_value_heads")

        if self.intermediate_size is None:
            self.intermediate_size = int(self.hidden_size * 4)

        if self.max_position_embeddings <= 0:
            raise ValueError("max_position_embeddings must be positive")

        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")

    @property
    def head_dim(self) -> int:
        return self.hidden_size // self.num_attention_heads

    @property
    def num_key_value_groups(self) -> int:
        return self.num_attention_heads // self.num_key_value_heads

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def tiny(cls, vocab_size: int = 4096) -> "EVUModelConfig":
        return cls(
            vocab_size=vocab_size,
            hidden_size=192,
            num_layers=4,
            num_attention_heads=6,
            num_key_value_heads=6,
            intermediate_size=768,
            max_position_embeddings=512,
        )

    @classmethod
    def small(cls, vocab_size: int = 4096) -> "EVUModelConfig":
        return cls(
            vocab_size=vocab_size,
            hidden_size=384,
            num_layers=8,
            num_attention_heads=6,
            num_key_value_heads=6,
            intermediate_size=1536,
            max_position_embeddings=1024,
        )