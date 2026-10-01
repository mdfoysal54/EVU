from __future__ import annotations

from dataclasses import dataclass

import torch

from .cache import GenerationCache
from .sampling import sample_next_token


@dataclass
class GenerationConfig:

    max_new_tokens: int = 128

    temperature: float = 0.8

    top_k: int | None = 50

    top_p: float = 0.95

    greedy: bool = False

    eos_token_id: int | None = None

    use_cache: bool = True


class EVUInferenceEngine:
    """Local inference engine with incremental KV-cache generation."""

    def __init__(
        self,
        model,
        tokenizer=None,
        device: str = "cpu",
    ) -> None:

        self.model = model.to(
            device
        )

        self.tokenizer = tokenizer

        self.device = torch.device(
            device
        )

        self.model.eval()

    def encode(
        self,
        prompt: str,
    ) -> torch.Tensor:

        if self.tokenizer is None:
            raise RuntimeError(
                "A tokenizer is required "
                "for text generation"
            )

        ids = self.tokenizer.encode(
            prompt
        )

        return torch.tensor(
            [ids],
            dtype=torch.long,
            device=self.device,
        )

    def _eos(
        self,
        config: GenerationConfig,
    ) -> int | None:

        if (
            config.eos_token_id
            is not None
        ):
            return config.eos_token_id

        return getattr(
            self.model.config,
            "eos_token_id",
            None,
        )

    @torch.no_grad()
    def generate_ids(
        self,
        input_ids: torch.Tensor,
        config: GenerationConfig | None = None,
    ) -> torch.Tensor:

        config = (
            config
            or GenerationConfig()
        )

        if input_ids.ndim != 2:
            raise ValueError(
                "input_ids must have shape "
                "[batch, sequence]"
            )

        generated = input_ids.to(
            self.device
        )

        max_context = int(
            self.model.config.max_position_embeddings
        )

        if (
            generated.shape[1]
            > max_context
        ):

            generated = (
                generated[
                    :,
                    -max_context:
                ]
            )

        eos = self._eos(
            config
        )

        if config.max_new_tokens <= 0:
            return generated

        cache = GenerationCache()

        context = (
            generated[
                :,
                -max_context:
            ]
        )

        output = self.model(
            context,
            attention_mask=torch.ones_like(
                context,
                dtype=torch.bool,
            ),
            use_cache=config.use_cache,
        )

        if config.use_cache:
            cache.update(
                output.past_key_values
            )

        for _ in range(
            config.max_new_tokens
        ):

            next_token = sample_next_token(
                output.logits[:, -1, :],
                temperature=config.temperature,
                top_k=config.top_k,
                top_p=config.top_p,
                greedy=config.greedy,
            )

            generated = torch.cat(
                [
                    generated,
                    next_token,
                ],
                dim=-1,
            )

            if (
                eos is not None
                and bool(
                    torch.all(
                        next_token == eos
                    )
                )
            ):
                break

            if not config.use_cache:

                context = (
                    generated[
                        :,
                        -max_context:
                    ]
                )

                output = self.model(
                    context,
                    attention_mask=torch.ones_like(
                        context,
                        dtype=torch.bool,
                    ),
                )

                continue

            if (
                cache.sequence_length
                >= max_context
            ):

                context = (
                    generated[
                        :,
                        -max_context:
                    ]
                )

                output = self.model(
                    context,
                    attention_mask=torch.ones_like(
                        context,
                        dtype=torch.bool,
                    ),
                    use_cache=True,
                )

                cache.update(
                    output.past_key_values
                )

                continue

            position = (
                cache.sequence_length
            )

            position_ids = torch.full(
                (
                    generated.shape[0],
                    1,
                ),
                position,
                dtype=torch.long,
                device=self.device,
            )

            key_mask = torch.ones(
                generated.shape[0],
                cache.sequence_length + 1,
                dtype=torch.bool,
                device=self.device,
            )

            output = self.model(
                next_token,
                attention_mask=key_mask,
                position_ids=position_ids,
                past_key_values=(
                    cache.past_key_values
                ),
                use_cache=True,
            )

            cache.update(
                output.past_key_values
            )

        return generated

    @torch.no_grad()
    def generate(
        self,
        prompt: str,
        config: GenerationConfig | None = None,
    ) -> str:

        if self.tokenizer is None:
            raise RuntimeError(
                "A tokenizer is required "
                "for text generation"
            )

        ids = self.encode(
            prompt
        )

        output = self.generate_ids(
            ids,
            config,
        )

        return self.tokenizer.decode(
            output[0].tolist(),
            skip_special_tokens=True,
        )