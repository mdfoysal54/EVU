from __future__ import annotations

import torch
from torch import nn

from .normalization import RMSNorm
from .transformer import TransformerBlock


class EVUDecoder(nn.Module):

    def __init__(
        self,
        config,
    ) -> None:

        super().__init__()

        self.layers = nn.ModuleList(
            [
                TransformerBlock(config)
                for _ in range(
                    config.num_layers
                )
            ]
        )

        self.norm = RMSNorm(
            config.hidden_size,
            config.rms_norm_eps,
        )

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.Tensor | None = None,
        past_key_values=None,
        use_cache: bool = False,
    ):

        presents = (
            []
            if use_cache
            else None
        )

        for index, layer in enumerate(
            self.layers
        ):

            past = (
                None
                if past_key_values is None
                else past_key_values[index]
            )

            hidden_states, present = layer(
                hidden_states,
                attention_mask=attention_mask,
                position_ids=position_ids,
                past_key_value=past,
                use_cache=use_cache,
            )

            if use_cache:
                presents.append(
                    present
                )

        return (
            self.norm(hidden_states),
            presents,
        )