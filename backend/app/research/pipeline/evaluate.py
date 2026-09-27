import math
import torch
from app.research.modeling.transformer import EVUTransformerLM


@torch.no_grad()
def evaluate_model(
    model: EVUTransformerLM,
    batches: list[torch.Tensor],
    device: str,
) -> dict:
    model.eval()
    losses = []

    for input_ids in batches:
        input_ids = input_ids.to(device)

        output = model(
            input_ids,
            labels=input_ids,
        )

        # Handle both dict-like and class/object outputs safely
        loss_val = (
            output["loss"]
            if isinstance(output, dict)
            else getattr(output, "loss", None)
        )

        if loss_val is not None:
            losses.append(float(loss_val.item()))

    if not losses:
        return {
            "loss": None,
            "perplexity": None,
        }

    average_loss = sum(losses) / len(losses)

    try:
        perplexity = math.exp(average_loss)
    except OverflowError:
        perplexity = float("inf")

    return {
        "loss": average_loss,
        "perplexity": perplexity,
    }