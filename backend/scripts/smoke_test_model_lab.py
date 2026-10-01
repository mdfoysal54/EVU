from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

import torch

from app.model_lab.architecture import EVUModelConfig, EVUTransformer
from app.model_lab.tokenizer import ByteBPETokenizer


def main() -> None:
    texts = [
        "EVU is an independent personal AI.",
        "EVU can use local models and optional external models.",
        "This is a tiny training corpus for a model smoke test.",
    ]
    tokenizer = ByteBPETokenizer()
    tokenizer.train(texts)

    config = EVUModelConfig.tiny(vocab_size=len(tokenizer))
    model = EVUTransformer(config)

    ids = torch.tensor([tokenizer.encode(texts[0])], dtype=torch.long)
    labels = ids.clone()
    output = model(ids, labels=labels)

    output.loss.backward()
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print("EVU MODEL LAB SMOKE TEST: PASS")
    print("vocab_size:", len(tokenizer))
    print("parameters:", sum(p.numel() for p in model.parameters()))
    print("trainable_parameters:", trainable)
    print("logits_shape:", tuple(output.logits.shape))
    print("loss:", float(output.loss))
    print("generated_ids:", model.generate(ids, max_new_tokens=8).tolist())


if __name__ == "__main__":
    main()