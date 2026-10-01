import json

import torch

from app.model_lab.architecture.config import (
    EVUModelConfig,
)

from app.model_lab.architecture.model import (
    EVUForCausalLM,
)

from app.model_lab.serving.bundle import (
    EVUModelBundle,
)

from app.model_lab.tokenizer.byte_bpe import (
    ByteBPETokenizer,
)


def test_model_bundle_load(
    tmp_path,
):

    tokenizer = ByteBPETokenizer()

    tokenizer.train(
        [
            "hello world",
            "Assistant: hello",
            "User: hello",
        ]
    )

    config = EVUModelConfig.tiny(
        vocab_size=len(tokenizer)
    )

    model = EVUForCausalLM(
        config
    )

    torch.save(
        {
            "model_state_dict": (
                model.state_dict()
            )
        },
        tmp_path / "model.pt",
    )

    tokenizer.save(
        tmp_path
        / "tokenizer.json"
    )

    (
        tmp_path
        / "config.json"
    ).write_text(
        json.dumps(
            config.to_dict()
        ),
        encoding="utf-8",
    )

    bundle = EVUModelBundle.load(
        tmp_path,
        device="cpu",
    )

    assert (
        bundle.config.vocab_size
        == len(tokenizer)
    )

    assert bundle.model is not None

    assert bundle.tokenizer is not None