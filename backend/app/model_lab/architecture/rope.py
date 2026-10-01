from __future__ import annotations

import torch
from torch import nn


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)


class RotaryEmbedding(nn.Module):
    """RoPE with cached cosine/sine tables."""

    def __init__(
        self,
        head_dim: int,
        max_position_embeddings: int = 2048,
        theta: float = 10000.0,
    ) -> None:
        super().__init__()
        if head_dim % 2:
            raise ValueError("RoPE requires an even head dimension")
        self.head_dim = head_dim
        self.theta = theta
        inv_freq = 1.0 / (
            theta ** (torch.arange(0, head_dim, 2).float() / head_dim)
        )
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self._build_cache(max_position_embeddings, torch.device("cpu"), torch.float32)

    def _build_cache(self, length: int, device: torch.device, dtype: torch.dtype) -> None:
        positions = torch.arange(length, device=device, dtype=self.inv_freq.dtype)
        freqs = torch.outer(positions, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.register_buffer("_cos_cached", emb.cos().to(dtype), persistent=False)
        self.register_buffer("_sin_cached", emb.sin().to(dtype), persistent=False)

    def _ensure_length(self, length: int, device: torch.device) -> None:
        if self._cos_cached.device != device or self._cos_cached.shape[0] < length:
            self._build_cache(max(length, self._cos_cached.shape[0] * 2), device, torch.float32)

    def forward(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        position_ids: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        seq_len = q.shape[-2]
        if position_ids is None:
            position_ids = torch.arange(seq_len, device=q.device).unsqueeze(0)

        max_pos = int(position_ids.max().item()) + 1
        self._ensure_length(max_pos, q.device)

        cos = self._cos_cached[position_ids].to(dtype=q.dtype)
        sin = self._sin_cached[position_ids].to(dtype=q.dtype)
        return (q * cos.unsqueeze(1)) + (rotate_half(q) * sin.unsqueeze(1)), (
            k * cos.unsqueeze(1)
        ) + (rotate_half(k) * sin.unsqueeze(1))