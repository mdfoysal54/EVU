from __future__ import annotations

from collections.abc import Iterator

import torch

from .cache import GenerationCache
from .engine import GenerationConfig
from .sampling import sample_next_token


@torch.no_grad()
def stream_generate(
    model,
    tokenizer,
    prompt: str,
    *,
    config: GenerationConfig | None = None,
) -> Iterator[str]:
    """True incremental local token streaming using KV cache."""

    config = (
        config
        or GenerationConfig()
    )

    device = next(
        model.parameters()
    ).device

    max_context = int(
        model.config.max_position_embeddings
    )

    eos = config.eos_token_id

    if eos is None:
        eos = model.config.eos_token_id

    ids = tokenizer.encode(
        prompt
    )

    generated = torch.tensor(
        [ids],
        dtype=torch.long,
        device=device,
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

    cache = GenerationCache()

    output = model(
        generated,
        attention_mask=torch.ones_like(
            generated,
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

        text = tokenizer.decode(
            next_token[0].tolist(),
            skip_special_tokens=True,
        )

        if text:
            yield text

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

            output = model(
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

            output = model(
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

        position_ids = torch.tensor(
            [[position]],
            dtype=torch.long,
            device=device,
        )

        key_mask = torch.ones(
            1,
            cache.sequence_length + 1,
            dtype=torch.bool,
            device=device,
        )

        output = model(
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