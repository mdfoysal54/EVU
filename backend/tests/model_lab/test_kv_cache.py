import torch

from app.model_lab.architecture import (
    EVUModelConfig,
    EVUTransformer,
)

from app.model_lab.inference import (
    EVUInferenceEngine,
    GenerationConfig,
)


def test_cached_and_uncached_greedy_generation_match():

    torch.manual_seed(7)

    config = EVUModelConfig.tiny(
        vocab_size=128
    )

    model = (
        EVUTransformer(config)
        .eval()
    )

    input_ids = torch.randint(
        0,
        config.vocab_size,
        (1, 12),
    )

    engine = EVUInferenceEngine(
        model,
        device="cpu",
    )

    cached = engine.generate_ids(
        input_ids,
        GenerationConfig(
            max_new_tokens=6,
            greedy=True,
            use_cache=True,
        ),
    )

    uncached = engine.generate_ids(
        input_ids,
        GenerationConfig(
            max_new_tokens=6,
            greedy=True,
            use_cache=False,
        ),
    )

    assert torch.equal(
        cached,
        uncached,
    )


def test_forward_cache_shapes():

    config = EVUModelConfig.tiny(
        vocab_size=128
    )

    model = (
        EVUTransformer(config)
        .eval()
    )

    ids = torch.randint(
        0,
        config.vocab_size,
        (2, 8),
    )

    first = model(
        ids,
        attention_mask=torch.ones_like(
            ids,
            dtype=torch.bool,
        ),
        use_cache=True,
    )

    assert (
        first.past_key_values
        is not None
    )

    assert len(
        first.past_key_values
    ) == config.num_layers

    next_ids = torch.randint(
        0,
        config.vocab_size,
        (2, 1),
    )

    second = model(
        next_ids,
        attention_mask=torch.ones(
            2,
            9,
            dtype=torch.bool,
        ),
        position_ids=torch.full(
            (2, 1),
            8,
            dtype=torch.long,
        ),
        past_key_values=(
            first.past_key_values
        ),
        use_cache=True,
    )

    assert second.logits.shape == (
        2,
        1,
        config.vocab_size,
    )

    assert (
        second
        .past_key_values[0][0]
        .shape[-2]
        == 9
    )