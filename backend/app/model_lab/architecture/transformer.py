from __future__ import annotations

import torch
from torch import nn

from .attention import GroupedQueryAttention
from .mlp import SwiGLU
from .normalization import RMSNorm


class TransformerBlock(nn.Module):
    def __init__(self, config) -> None:
        super().__init__()
        self.input_norm = RMSNorm(config.hidden_size, config.rms_norm_eps)
        self.attention = GroupedQueryAttention(config)
        self.post_attention_norm = RMSNorm(config.hidden_size, config.rms_norm_eps)
        self.mlp = SwiGLU(
            config.hidden_size,
            config.intermediate_size,
            bias=config.mlp_bias,
            dropout=config.dropout,
        )

    def forward(
        self,
        x: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.Tensor | None = None,
        past_key_value=None,
        use_cache: bool = False,
    ):
        attn_out, present = self.attention(
            self.input_norm(x),
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_value=past_key_value,
            use_cache=use_cache,
        )
        x = x + attn_out
        x = x + self.mlp(self.post_attention_norm(x))
        return x, present