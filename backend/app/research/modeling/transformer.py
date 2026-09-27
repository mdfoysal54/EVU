import math
from typing import Any, Dict, Optional

import torch
from torch import nn

from app.research.modeling.config import EVUModelConfig


class EVURMSNorm(nn.Module):

    def __init__(
        self,
        hidden_size: int,
        eps: float = 1e-6,
    ):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        input_dtype = x.dtype
        variance = x.float().pow(2).mean(dim=-1, keepdim=True)
        x_normed = x.float() * torch.rsqrt(variance + self.eps)
        return (self.weight * x_normed).to(input_dtype)


class EVUSelfAttention(nn.Module):

    def __init__(
        self,
        config: EVUModelConfig,
    ):
        super().__init__()
        self.num_heads = config.num_attention_heads
        self.head_dim = config.head_dim
        self.hidden_size = config.hidden_size
        self.all_head_size = self.num_heads * self.head_dim

        self.q_proj = nn.Linear(
            config.hidden_size,
            self.all_head_size,
            bias=False,
        )
        self.k_proj = nn.Linear(
            config.hidden_size,
            self.all_head_size,
            bias=False,
        )
        self.v_proj = nn.Linear(
            config.hidden_size,
            self.all_head_size,
            bias=False,
        )
        self.o_proj = nn.Linear(
            self.all_head_size,
            config.hidden_size,
            bias=False,
        )
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape

        q = self.q_proj(x)
        k = self.k_proj(x)
        v = self.v_proj(x)

        q = q.view(
            batch_size, seq_len, self.num_heads, self.head_dim
        ).transpose(1, 2)
        k = k.view(
            batch_size, seq_len, self.num_heads, self.head_dim
        ).transpose(1, 2)
        v = v.view(
            batch_size, seq_len, self.num_heads, self.head_dim
        ).transpose(1, 2)

        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        causal_mask = torch.triu(
            torch.ones(
                seq_len,
                seq_len,
                device=x.device,
                dtype=torch.bool,
            ),
            diagonal=1,
        )

        scores = scores.masked_fill(causal_mask, float("-inf"))
        attention = torch.softmax(scores, dim=-1)
        attention = self.dropout(attention)

        output = attention @ v
        output = output.transpose(1, 2).contiguous()
        output = output.view(batch_size, seq_len, self.all_head_size)

        return self.o_proj(output)


class EVUFeedForward(nn.Module):

    def __init__(
        self,
        config: EVUModelConfig,
    ):
        super().__init__()
        self.gate = nn.Linear(
            config.hidden_size,
            config.intermediate_size,
            bias=False,
        )
        self.up = nn.Linear(
            config.hidden_size,
            config.intermediate_size,
            bias=False,
        )
        self.down = nn.Linear(
            config.intermediate_size,
            config.hidden_size,
            bias=False,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.down(
            nn.functional.silu(self.gate(x)) * self.up(x)
        )


class EVUTransformerBlock(nn.Module):

    def __init__(
        self,
        config: EVUModelConfig,
    ):
        super().__init__()
        self.norm1 = EVURMSNorm(config.hidden_size)
        self.attention = EVUSelfAttention(config)
        self.norm2 = EVURMSNorm(config.hidden_size)
        self.feed_forward = EVUFeedForward(config)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attention(self.norm1(x))
        x = x + self.feed_forward(self.norm2(x))
        return x


class EVUTransformerLM(nn.Module):

    def __init__(
        self,
        config: EVUModelConfig,
    ):
        super().__init__()
        self.config = config

        self.token_embedding = nn.Embedding(
            config.vocab_size,
            config.hidden_size,
        )
        self.position_embedding = nn.Embedding(
            config.max_sequence_length,
            config.hidden_size,
        )
        self.dropout = nn.Dropout(config.dropout)
        self.layers = nn.ModuleList(
            [
                EVUTransformerBlock(config)
                for _ in range(config.num_layers)
            ]
        )
        self.norm = EVURMSNorm(config.hidden_size)
        self.lm_head = nn.Linear(
            config.hidden_size,
            config.vocab_size,
            bias=False,
        )

        # Weight tying
        self.lm_head.weight = self.token_embedding.weight

        self.apply(self._initialize_weights)

    def _initialize_weights(self, module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(
        self,
        input_ids: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
    ) -> Dict[str, Any]:
        batch_size, seq_len = input_ids.shape

        if seq_len > self.config.max_sequence_length:
            raise ValueError(
                f"Sequence length ({seq_len}) exceeds model limit ({self.config.max_sequence_length})."
            )

        positions = torch.arange(
            seq_len,
            device=input_ids.device,
            dtype=torch.long,
        ).unsqueeze(0)

        x = self.token_embedding(input_ids) + self.position_embedding(positions)
        x = self.dropout(x)

        for layer in self.layers:
            x = layer(x)

        x = self.norm(x)
        logits = self.lm_head(x)

        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss = nn.functional.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
            )

        return {
            "logits": logits,
            "loss": loss,
        }

    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 100,
        temperature: float = 0.8,
        top_k: int = 50,
    ) -> torch.Tensor:
        self.eval()

        for _ in range(max_new_tokens):
            context = input_ids[:, -self.config.max_sequence_length :]
            output = self.forward(context)

            logits = output["logits"][:, -1, :]
            logits = logits / max(temperature, 1e-5)

            if top_k > 0:
                k_val = min(top_k, logits.size(-1))
                values, _ = torch.topk(logits, k_val)
                cutoff = values[:, -1].unsqueeze(-1)
                logits = torch.where(
                    logits < cutoff,
                    torch.full_like(logits, float("-inf")),
                    logits,
                )

            probabilities = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probabilities, num_samples=1)
            input_ids = torch.cat([input_ids, next_token], dim=1)

        return input_ids