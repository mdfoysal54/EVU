from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from .config import EVUModelConfig
from .decoder import EVUDecoder
from .embeddings import TokenEmbedding
from .lm_head import LMHead


@dataclass
class EVUModelOutput:
    logits: torch.Tensor
    loss: torch.Tensor | None = None
    past_key_values: tuple | None = None


class EVUTransformer(nn.Module):
    """EVU's owned decoder-only causal language model.

    Block 3 adds real incremental KV-cache generation.
    """

    def __init__(
        self,
        config: EVUModelConfig,
    ) -> None:
        super().__init__()
        self.config = config

        self.embed_tokens = TokenEmbedding(
            config.vocab_size,
            config.hidden_size,
        )

        self.decoder = EVUDecoder(config)

        self.lm_head = LMHead(
            config.hidden_size,
            config.vocab_size,
            (
                self.embed_tokens.embedding
                if config.tie_word_embeddings
                else None
            ),
        )

        self._init_weights()

    def _init_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(
                    module.weight,
                    mean=0.0,
                    std=self.config.initializer_range,
                )
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

            elif isinstance(module, nn.Embedding):
                nn.init.normal_(
                    module.weight,
                    mean=0.0,
                    std=self.config.initializer_range,
                )

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        labels: torch.Tensor | None = None,
        position_ids: torch.Tensor | None = None,
        past_key_values=None,
        use_cache: bool = False,
    ) -> EVUModelOutput:
        if input_ids.dtype != torch.long:
            input_ids = input_ids.long()

        if input_ids.ndim != 2:
            raise ValueError(
                "input_ids must have shape [batch, sequence]"
            )

        if input_ids.shape[1] == 0:
            raise ValueError(
                "input_ids must contain at least one token"
            )

        past_len = 0
        if past_key_values is not None:
            if len(past_key_values) != self.config.num_layers:
                raise ValueError(
                    "past_key_values length does not match model layers"
                )
            past_len = int(past_key_values[0][0].shape[-2])

        if (
            input_ids.shape[1] + past_len
            > self.config.max_position_embeddings
        ):
            raise ValueError(
                "input plus KV-cache length exceeds max_position_embeddings; "
                "restart generation from a truncated context"
            )

        hidden = self.embed_tokens(input_ids)

        hidden, presents = self.decoder(
            hidden,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            use_cache=use_cache,
        )

        logits = self.lm_head(hidden)

        loss = None
        if labels is not None:
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = labels[:, 1:].contiguous()
            loss = torch.nn.functional.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
            )

        return EVUModelOutput(
            logits=logits,
            loss=loss,
            past_key_values=(
                tuple(presents) if presents is not None else None
            ),
        )

    @staticmethod
    def _sample(
        logits: torch.Tensor,
        *,
        temperature: float,
        top_k: int | None,
        top_p: float,
        greedy: bool,
    ) -> torch.Tensor:
        if greedy or temperature <= 0:
            return logits.argmax(dim=-1, keepdim=True)

        logits = logits / temperature

        if top_k is not None and top_k > 0:
            k = min(int(top_k), logits.shape[-1])
            values, _ = torch.topk(logits, k)
            cutoff = values[:, -1:].contiguous()
            logits = logits.masked_fill(logits < cutoff, float("-inf"))

        if 0.0 < top_p < 1.0:
            sorted_logits, sorted_indices = torch.sort(
                logits, descending=True
            )
            probs = torch.softmax(sorted_logits, dim=-1)
            cumulative = torch.cumsum(probs, dim=-1)

            remove = cumulative > top_p
            remove[:, 1:] = remove[:, :-1].clone()
            remove[:, 0] = False

            sorted_logits = sorted_logits.masked_fill(
                remove, float("-inf")
            )
            logits = torch.full_like(logits, float("-inf"))
            logits.scatter_(1, sorted_indices, sorted_logits)

        return torch.multinomial(torch.softmax(logits, dim=-1), 1)

    @staticmethod
    def _truncate_cache(
        past_key_values,
        keep_tokens: int,
    ):
        if past_key_values is None:
            return None

        return tuple(
            (
                key[:, :, -keep_tokens:, :].contiguous(),
                value[:, :, -keep_tokens:, :].contiguous(),
            )
            for key, value in past_key_values
        )

    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        *,
        max_new_tokens: int = 64,
        temperature: float = 1.0,
        top_k: int | None = 50,
        top_p: float = 0.95,
        eos_token_id: int | None = None,
        greedy: bool = False,
        use_cache: bool = True,
    ) -> torch.Tensor:
        self.eval()

        if input_ids.ndim != 2:
            raise ValueError(
                "input_ids must have shape [batch, sequence]"
            )

        if max_new_tokens < 0:
            raise ValueError("max_new_tokens cannot be negative")

        device = next(self.parameters()).device
        generated = input_ids.to(device)

        if generated.shape[1] > self.config.max_position_embeddings:
            generated = generated[
                :, -self.config.max_position_embeddings :
            ]

        eos = (
            self.config.eos_token_id
            if eos_token_id is None
            else eos_token_id
        )

        if max_new_tokens == 0:
            return generated

        # -------------------------------------------------
        # Compatibility / reference path
        # -------------------------------------------------
        if not use_cache:
            for _ in range(max_new_tokens):
                context = generated[
                    :, -self.config.max_position_embeddings :
                ]
                output = self(
                    context,
                    attention_mask=torch.ones_like(
                        context, dtype=torch.bool
                    ),
                )
                next_token = self._sample(
                    output.logits[:, -1, :],
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    greedy=greedy,
                )
                generated = torch.cat((generated, next_token), dim=-1)

                if eos is not None and bool(
                    torch.all(next_token == eos)
                ):
                    break

            return generated

        # -------------------------------------------------
        # KV-cache path
        # -------------------------------------------------
        context = generated[:, -self.config.max_position_embeddings :]
        initial_mask = torch.ones_like(context, dtype=torch.bool)
        output = self(
            context,
            attention_mask=initial_mask,
            use_cache=True,
        )
        past = output.past_key_values

        for _ in range(max_new_tokens):
            next_token = self._sample(
                output.logits[:, -1, :],
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                greedy=greedy,
            )
            generated = torch.cat((generated, next_token), dim=-1)

            if eos is not None and bool(torch.all(next_token == eos)):
                break

            past_len = int(past[0][0].shape[-2])

            # Context window reached: re-prefill instead of overflowing
            if past_len >= self.config.max_position_embeddings:
                context = generated[
                    :, -self.config.max_position_embeddings :
                ]
                output = self(
                    context,
                    attention_mask=torch.ones_like(
                        context, dtype=torch.bool
                    ),
                    use_cache=True,
                )
                past = output.past_key_values
                continue

            position_ids = torch.full(
                (generated.shape[0], 1),
                past_len,
                dtype=torch.long,
                device=generated.device,
            )

            key_mask = torch.ones(
                generated.shape[0],
                past_len + 1,
                dtype=torch.bool,
                device=generated.device,
            )

            output = self(
                next_token,
                attention_mask=key_mask,
                position_ids=position_ids,
                past_key_values=past,
                use_cache=True,
            )
            past = output.past_key_values

        return generated


EVUForCausalLM = EVUTransformer
EVUForCausalLM = EVUTransformer
