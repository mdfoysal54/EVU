from __future__ import annotations

import math
import torch
from torch.utils.data import DataLoader


@torch.no_grad()
def evaluate_perplexity(model, dataloader: DataLoader, device: str | torch.device = "cpu") -> dict:
    model.eval()
    device = torch.device(device)
    model.to(device)
    losses: list[float] = []
    tokens = 0

    for batch in dataloader:
        input_ids = batch.input_ids.to(device)
        labels = batch.labels.to(device)
        mask = batch.attention_mask.to(device)
        output = model(input_ids, attention_mask=mask, labels=labels)
        if output.loss is None:
            raise RuntimeError("Model did not return loss")
        valid = (labels[:, 1:] != -100).sum().item()
        losses.append(float(output.loss.cpu()) * max(valid, 1))
        tokens += max(valid, 1)

    mean_loss = sum(losses) / max(tokens, 1)
    return {
        "loss": mean_loss,
        "perplexity": math.exp(min(mean_loss, 50.0)),
        "tokens": tokens,
    }