from __future__ import annotations

from dataclasses import dataclass

import torch

from .cache import GenerationCache
from .sampling import sample_next_token


@dataclass
class BatchGenerationRequest:

    prompt: str

    max_new_tokens: int = 64

    temperature: float = 0.8

    top_k: int | None = 50

    top_p: float = 0.95

    greedy: bool = False


def pad_prompts(
    token_id_sequences: list[list[int]],
    pad_token_id: int,
) -> tuple[
    torch.Tensor,
    torch.Tensor,
]:

    if not token_id_sequences:
        raise ValueError(
            "token_id_sequences "
            "cannot be empty"
        )

    if any(
        not seq
        for seq in token_id_sequences
    ):
        raise ValueError(
            "prompt sequences "
            "cannot be empty"
        )

    max_len = max(
        map(
            len,
            token_id_sequences,
        )
    )

    ids = []
    masks = []

    for seq in token_id_sequences:

        pad = (
            max_len
            - len(seq)
        )

        # Left padding is intentional.
        #
        # It ensures the last position
        # in every row is the final
        # actual prompt token.

        ids.append(
            [pad_token_id] * pad
            + seq
        )

        masks.append(
            [0] * pad
            + [1] * len(seq)
        )

    return (
        torch.tensor(
            ids,
            dtype=torch.long,
        ),
        torch.tensor(
            masks,
            dtype=torch.bool,
        ),
    )


@torch.no_grad()
def generate_batch(
    model,
    token_batches: list[list[int]],
    *,
    pad_token_id: int,
    eos_token_id: int | None = None,
    max_new_tokens: int = 64,
    temperature: float = 0.8,
    top_k: int | None = 50,
    top_p: float = 0.95,
    greedy: bool = False,
    use_cache: bool = True,
) -> list[list[int]]:

    if not token_batches:
        return []

    if max_new_tokens < 0:
        raise ValueError(
            "max_new_tokens "
            "cannot be negative"
        )

    device = next(
        model.parameters()
    ).device

    input_ids, attention_mask = (
        pad_prompts(
            token_batches,
            pad_token_id,
        )
    )

    input_ids = input_ids.to(
        device
    )

    attention_mask = (
        attention_mask.to(device)
    )

    generated = [
        list(seq)
        for seq in token_batches
    ]

    output = model(
        input_ids,
        attention_mask=attention_mask,
        use_cache=use_cache,
    )

    cache = GenerationCache()

    if use_cache:

        cache.update(
            output.past_key_values
        )

    finished = torch.zeros(
        len(token_batches),
        dtype=torch.bool,
        device=device,
    )

    eos = eos_token_id

    for _ in range(
        max_new_tokens
    ):

        next_token = sample_next_token(
            output.logits[:, -1, :],
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            greedy=greedy,
        )

        if eos is not None:

            next_token = torch.where(
                finished[:, None],
                torch.full_like(
                    next_token,
                    eos,
                ),
                next_token,
            )

        for row, token in enumerate(
            next_token[:, 0].tolist()
        ):

            if not finished[row]:
                generated[row].append(
                    int(token)
                )

        if eos is not None:

            finished = (
                finished
                | next_token[:, 0].eq(eos)
            )

            if bool(
                torch.all(finished)
            ):
                break

        if not use_cache:

            max_context = int(
                model.config.max_position_embeddings
            )

            padded, mask = pad_prompts(
                generated,
                pad_token_id,
            )

            padded = (
                padded[
                    :,
                    -max_context:
                ]
                .to(device)
            )

            mask = (
                mask[
                    :,
                    -max_context:
                ]
                .to(device)
            )

            output = model(
                padded,
                attention_mask=mask,
            )

            continue

        if (
            cache.sequence_length
            >= model.config.max_position_embeddings
        ):

            max_context = int(
                model.config.max_position_embeddings
            )

            padded, mask = pad_prompts(
                generated,
                pad_token_id,
            )

            padded = (
                padded[
                    :,
                    -max_context:
                ]
                .to(device)
            )

            mask = (
                mask[
                    :,
                    -max_context:
                ]
                .to(device)
            )

            output = model(
                padded,
                attention_mask=mask,
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
                len(token_batches),
                1,
            ),
            position,
            dtype=torch.long,
            device=device,
        )

        key_mask = torch.ones(
            len(token_batches),
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

    return generated