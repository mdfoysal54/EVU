from app.model_lab.tokenizer import ByteBPETokenizer


def test_byte_bpe_round_trip():
    tokenizer = ByteBPETokenizer()
    texts = ["Hello EVU!", "বাংলা ভাষা", "local AI works."]
    tokenizer.train(texts)
    for text in texts:
        assert tokenizer.decode(tokenizer.encode(text)) == text


def test_tokenizer_serialization(tmp_path):
    tokenizer = ByteBPETokenizer()
    tokenizer.train(["EVU model lab", "local inference"])
    path = tmp_path / "tokenizer.json"
    tokenizer.save(path)
    loaded = ByteBPETokenizer.load(path)
    assert loaded.decode(loaded.encode("EVU model lab")) == "EVU model lab"