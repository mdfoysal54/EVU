from __future__ import annotations

import torch


class PackedCausalCollator:
    def __init__(self, pad_token_id: int):
        self.pad_token_id = pad_token_id

    def __call__(
        self,
        examples: list[dict],
    ) -> dict[str, torch.Tensor]:
        max_length = max(
            len(item["input_ids"])
            for item in examples
        )

        input_ids = []
        labels = []
        attention_masks = []

        for item in examples:
            ids = list(item["input_ids"])
            target = list(
                item.get(
                    "labels",
                    ids,
                )
            )

            padding = max_length - len(ids)

            input_ids.append(
                ids + [self.pad_token_id] * padding
            )

            labels.append(
                target + [-100] * padding
            )

            attention_masks.append(
                [1] * len(ids) + [0] * padding
            )

        return {
            "input_ids": torch.tensor(
                input_ids,
                dtype=torch.long,
            ),
            "labels": torch.tensor(
                labels,
                dtype=torch.long,
            ),
            "attention_mask": torch.tensor(
                attention_masks,
                dtype=torch.bool,
            ),
        }