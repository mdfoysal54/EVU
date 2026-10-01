import torch

from app.model_lab.architecture import EVUModelConfig, EVUTransformer


def test_tiny_forward_backward():
    config = EVUModelConfig.tiny(vocab_size=128)
    model = EVUTransformer(config)
    input_ids = torch.randint(0, config.vocab_size, (2, 16))
    out = model(input_ids, labels=input_ids)
    assert out.logits.shape == (2, 16, config.vocab_size)
    assert out.loss is not None
    out.loss.backward()
    assert any(p.grad is not None for p in model.parameters())


def test_generation_shape():
    config = EVUModelConfig.tiny(vocab_size=128)
    model = EVUTransformer(config)
    input_ids = torch.randint(0, config.vocab_size, (1, 5))
    output = model.generate(input_ids, max_new_tokens=3)
    assert output.shape == (1, 8)