from __future__ import annotations

import math

import torch
from torch import nn
from torch.nn import functional as F

from .rope import RotaryEmbedding


class GroupedQueryAttention(nn.Module):
    """Causal self-attention with GQA, SDPA/flash dispatch and KV caching.

    torch.nn.functional.scaled_dot_product_attention is used when available.
    On supported CUDA builds PyTorch can dispatch this to optimized
    Flash/Memory-Efficient kernels automatically.

    A manual implementation remains available as a correctness fallback.
    """

    def __init__(self, config) -> None:
        super().__init__()

        self.num_heads = config.num_attention_heads
        self.num_kv_heads = config.num_key_value_heads
        self.num_groups = config.num_key_value_groups
        self.head_dim = config.head_dim

        hidden = config.hidden_size

        self.q_proj = nn.Linear(
            hidden,
            self.num_heads * self.head_dim,
            bias=config.attention_bias,
        )

        self.k_proj = nn.Linear(
            hidden,
            self.num_kv_heads * self.head_dim,
            bias=config.attention_bias,
        )

        self.v_proj = nn.Linear(
            hidden,
            self.num_kv_heads * self.head_dim,
            bias=config.attention_bias,
        )

        self.o_proj = nn.Linear(
            hidden,
            hidden,
            bias=config.attention_bias,
        )

        self.dropout = nn.Dropout(config.dropout)

        self.rope = RotaryEmbedding(
            self.head_dim,
            config.max_position_embeddings,
            config.rope_theta,
        )

    def _shape(
        self,
        x: torch.Tensor,
        heads: int,
    ) -> torch.Tensor:

        batch, seq_len, _ = x.shape

        return (
            x.view(
                batch,
                seq_len,
                heads,
                self.head_dim,
            )
            .transpose(1, 2)
        )

    def _expand_kv(
        self,
        k: torch.Tensor,
        v: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:

        if self.num_groups == 1:
            return k, v

        return (
            k.repeat_interleave(
                self.num_groups,
                dim=1,
            ),
            v.repeat_interleave(
                self.num_groups,
                dim=1,
            ),
        )

    @staticmethod
    def _key_padding_mask(
        attention_mask: torch.Tensor,
        batch: int,
        key_len: int,
        device: torch.device,
    ) -> torch.Tensor:

        if attention_mask.dtype != torch.bool:
            attention_mask = attention_mask != 0

        if attention_mask.ndim == 2:

            if attention_mask.shape != (
                batch,
                key_len,
            ):
                raise ValueError(
                    "2D attention_mask must have shape "
                    "[batch, key_length]"
                )

            return attention_mask[
                :,
                None,
                None,
                :,
            ]

        if attention_mask.ndim == 4:
            return attention_mask.to(
                device=device,
                dtype=torch.bool,
            )

        raise ValueError(
            "attention_mask must be [B,K] or [B,1,Q,K]"
        )

    def _manual_attention(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        allow: torch.Tensor,
    ) -> torch.Tensor:

        scores = torch.matmul(
            q,
            k.transpose(-2, -1),
        )

        scores = scores * (
            1.0 / math.sqrt(self.head_dim)
        )

        scores = scores.masked_fill(
            ~allow,
            torch.finfo(scores.dtype).min,
        )

        weights = torch.softmax(
            scores,
            dim=-1,
        )

        weights = self.dropout(weights)

        return torch.matmul(
            weights,
            v,
        )

    def _sdpa_attention(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        allow: torch.Tensor | None,
        *,
        is_causal: bool,
    ) -> torch.Tensor:

        dropout_p = (
            self.dropout.p
            if self.training
            else 0.0
        )

        try:

            return F.scaled_dot_product_attention(
                q,
                k,
                v,
                attn_mask=allow,
                dropout_p=dropout_p,
                is_causal=is_causal,
            )

        except (
            RuntimeError,
            NotImplementedError,
        ):

            if allow is None:

                batch, _, query_len, _ = q.shape
                key_len = k.shape[-2]

                query_positions = torch.arange(
                    query_len,
                    device=q.device,
                )

                key_positions = torch.arange(
                    key_len,
                    device=q.device,
                )

                allow = (
                    key_positions[None, :]
                    <= (
                        key_len
                        - query_len
                        + query_positions[:, None]
                    )
                )

                allow = (
                    allow[
                        None,
                        None,
                        :,
                        :
                    ]
                    .expand(
                        batch,
                        1,
                        query_len,
                        key_len,
                    )
                )

            return self._manual_attention(
                q,
                k,
                v,
                allow,
            )

    def forward(
        self,
        x: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.Tensor | None = None,
        past_key_value: (
            tuple[
                torch.Tensor,
                torch.Tensor,
            ]
            | None
        ) = None,
        use_cache: bool = False,
    ) -> tuple[
        torch.Tensor,
        tuple[
            torch.Tensor,
            torch.Tensor,
        ]
        | None,
    ]:

        q = self._shape(
            self.q_proj(x),
            self.num_heads,
        )

        k = self._shape(
            self.k_proj(x),
            self.num_kv_heads,
        )

        v = self._shape(
            self.v_proj(x),
            self.num_kv_heads,
        )

        past_len = (
            0
            if past_key_value is None
            else past_key_value[0].shape[-2]
        )

        if position_ids is None:

            position_ids = torch.arange(
                past_len,
                past_len + x.shape[1],
                device=x.device,
            ).unsqueeze(0)

            position_ids = position_ids.expand(
                x.shape[0],
                -1,
            )

        q, k = self.rope(
            q,
            k,
            position_ids,
        )

        if past_key_value is not None:

            past_k, past_v = past_key_value

            if past_k.shape[0] != k.shape[0]:
                raise ValueError(
                    "past_key_value batch size "
                    "does not match input"
                )

            k = torch.cat(
                (
                    past_k,
                    k,
                ),
                dim=-2,
            )

            v = torch.cat(
                (
                    past_v,
                    v,
                ),
                dim=-2,
            )

        present = (
            (k, v)
            if use_cache
            else None
        )

        k, v = self._expand_kv(
            k,
            v,
        )

        query_len = q.shape[-2]
        key_len = k.shape[-2]

        # Fast path:
        # no padding mask and no cache.
        #
        # This lets PyTorch select its most
        # optimized causal attention kernel.
        if (
            attention_mask is None
            and past_len == 0
        ):

            context = self._sdpa_attention(
                q,
                k,
                v,
                None,
                is_causal=True,
            )

        else:

            key_positions = torch.arange(
                key_len,
                device=x.device,
            )

            query_positions = (
                past_len
                + torch.arange(
                    query_len,
                    device=x.device,
                )
            )

            causal_allow = (
                key_positions[None, :]
                <= query_positions[:, None]
            )

            allow = causal_allow[
                None,
                None,
                :,
                :
            ]

            if attention_mask is not None:

                padding_allow = self._key_padding_mask(
                    attention_mask,
                    x.shape[0],
                    key_len,
                    x.device,
                )

                allow = (
                    allow
                    & padding_allow
                )

            context = self._sdpa_attention(
                q,
                k,
                v,
                allow,
                is_causal=False,
            )

        output = (
            context
            .transpose(1, 2)
            .contiguous()
            .view(
                x.shape[0],
                x.shape[1],
                -1,
            )
        )

        return self.o_proj(output), present