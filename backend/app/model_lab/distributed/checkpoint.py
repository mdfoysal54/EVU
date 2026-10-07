from __future__ import annotations

from pathlib import Path

import torch


def save_distributed_checkpoint(
    model,
    optimizer,
    path: str | Path,
    *,
    epoch: int,
    global_step: int,
) -> None:
    output = Path(path)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target = (
        model.module
        if hasattr(model, "module")
        else model
    )

    torch.save(
        {
            "model": target.state_dict(),
            "optimizer": optimizer.state_dict(),
            "epoch": epoch,
            "global_step": global_step,
        },
        output,
    )


def load_distributed_checkpoint(
    model,
    optimizer,
    path: str | Path,
    *,
    map_location="cpu",
) -> dict:
    checkpoint = torch.load(
        path,
        map_location=map_location,
    )

    target = (
        model.module
        if hasattr(model, "module")
        else model
    )

    target.load_state_dict(
        checkpoint["model"]
    )

    optimizer.load_state_dict(
        checkpoint["optimizer"]
    )

    return checkpoint