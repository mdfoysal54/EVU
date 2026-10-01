import torch

from app.model_lab.architecture import (
    EVUModelConfig,
    EVUTransformer,
)

from app.model_lab.inference.quantization import (
    quantize_dynamic_int8,
)


def test_dynamic_int8_quantization_runs_on_cpu():

    config = EVUModelConfig.tiny(
        vocab_size=64
    )

    model = (
        EVUTransformer(config)
        .eval()
    )

    quantized = (
        quantize_dynamic_int8(
            model
        )
    )

    ids = torch.randint(
        0,
        config.vocab_size,
        (1, 6),
    )

    output = quantized(
        ids
    )

    assert output.logits.shape == (
        1,
        6,
        config.vocab_size,
    )