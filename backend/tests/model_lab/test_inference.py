from app.model_lab.architecture import EVUModelConfig, EVUTransformer
from app.model_lab.inference import EVUInferenceEngine
from app.model_lab.tokenizer import ByteBPETokenizer


def test_inference_engine():
    tokenizer = ByteBPETokenizer()
    tokenizer.train(["EVU is local."])
    model = EVUTransformer(EVUModelConfig.tiny(vocab_size=len(tokenizer)))
    engine = EVUInferenceEngine(model, tokenizer)
    text = engine.generate("EVU", config=None)
    assert isinstance(text, str)