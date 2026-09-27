from pathlib import Path
from typing import Any, Tuple

import torch

from app.research.modeling.config import EVUModelConfig
from app.research.modeling.transformer import EVUTransformerLM


def save_checkpoint(
    model: EVUTransformerLM,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    step: int,
    loss: float,
    path: str,
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Unwrap DDP/DataParallel if wrapped
    raw_model = getattr(model, "module", model)

    torch.save(
        {
            "model_state_dict": raw_model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "epoch": epoch,
            "step": step,
            "loss": loss,
            "config": raw_model.config.to_dict(),
        },
        target,
    )


def load_checkpoint(
    path: str,
    device: str = "cpu",
) -> Tuple[EVUTransformerLM, torch.optim.Optimizer, dict[str, Any]]:
    checkpoint = torch.load(
        path,
        map_location=device,
        weights_only=False,
    )

    config = EVUModelConfig(**checkpoint["config"])
    model = EVUTransformerLM(config).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=1e-4,
    )

    if "optimizer_state_dict" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

    return model, optimizer, checkpoint