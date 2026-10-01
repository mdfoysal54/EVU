from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import torch
    from torch import Tensor
    import torch.nn as nn
else:
    try:
        import torch
        from torch import Tensor
        import torch.nn as nn
    except ImportError:  # pragma: no cover
        torch = None
        Tensor = Any
        nn = None


if nn is not None:
    class FeedForward(nn.Module):
        def __init__(
            self,
            hidden_size: int,
            intermediate_size: int,
            dropout: float = 0.0,
            activation: str = "gelu",
        ) -> None:
            super().__init__()
            activations = {
                "gelu": nn.GELU(),
                "relu": nn.ReLU(),
                "silu": nn.SiLU(),
            }
            if activation not in activations:
                raise ValueError(f"Unsupported activation: {activation}")
            self.fc1 = nn.Linear(hidden_size, intermediate_size)
            self.activation = activations[activation]
            self.fc2 = nn.Linear(intermediate_size, hidden_size)
            self.dropout = nn.Dropout(dropout)

        def forward(self, x: Tensor) -> Tensor:
            return self.dropout(self.fc2(self.activation(self.fc1(x))))

    class GatedFeedForward(nn.Module):
        def __init__(
            self,
            hidden_size: int,
            intermediate_size: int,
            dropout: float = 0.0,
        ) -> None:
            super().__init__()
            self.gate = nn.Linear(hidden_size, intermediate_size)
            self.up = nn.Linear(hidden_size, intermediate_size)
            self.down = nn.Linear(intermediate_size, hidden_size)
            self.dropout = nn.Dropout(dropout)

        def forward(self, x: Tensor) -> Tensor:
            gated = nn.functional.silu(self.gate(x)) * self.up(x)
            return self.dropout(self.down(gated))
else:
    class FeedForward:  # type: ignore
        def __init__(self, *_: object, **__: object) -> None:
            raise ImportError("PyTorch is required for model_lab architecture modules")

    GatedFeedForward = FeedForward