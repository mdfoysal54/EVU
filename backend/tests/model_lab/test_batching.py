import torch

from app.model_lab.architecture import (
    EVUModelConfig,
    EVUTransformer,
)

from app.model_lab.inference.batching import (
    generate_batch,
    pad_prompts,
)


def test_left_padding():

    ids, mask = pad_prompts(
        [
            [1, 2, 3],
            [4, 5],
        ],
        pad_token_id=0,
    )

    assert ids.tolist() == [
        [1, 2, 3],
        [0, 4, 5],
    ]

    assert mask.tolist() == [
        [True, True, True],
        [False, True, True],
    ]


def test_batch_generation_returns_one_result_per_prompt():

    torch.manual_seed(11)

    config = EVUModelConfig.tiny(
        vocab_size=64
    )

    model = (
        EVUTransformer(config)
        .eval()
    )

    results = generate_batch(
        model,
        [
            [1, 2, 3],
            [4, 5],
        ],
        pad_token_id=0,
        max_new_tokens=2,
        greedy=True,
    )

    assert len(results) == 2

    assert len(results[0]) >= 3

    assert len(results[1]) >= 2