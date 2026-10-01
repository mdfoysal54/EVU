from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import torch

from ..architecture.config import (
    EVUModelConfig,
)

from ..architecture.model import (
    EVUForCausalLM,
)

from ..tokenizer.byte_bpe import (
    ByteBPETokenizer,
)


@dataclass
class EVUModelBundle:

    model: EVUForCausalLM

    tokenizer: ByteBPETokenizer

    config: EVUModelConfig

    checkpoint_path: Path

    @classmethod
    def load(
        cls,
        bundle_dir: str | Path,
        *,
        device: str = "cpu",
    ) -> "EVUModelBundle":

        bundle_dir = Path(
            bundle_dir
        )

        config_path = (
            bundle_dir
            / "config.json"
        )

        tokenizer_path = (
            bundle_dir
            / "tokenizer.json"
        )

        checkpoint_path = (
            bundle_dir
            / "model.pt"
        )

        required = (
            config_path,
            tokenizer_path,
            checkpoint_path,
        )

        for path in required:

            if not path.exists():
                raise FileNotFoundError(
                    f"EVU model bundle is missing: {path}"
                )

        config_data = json.loads(
            config_path.read_text(
                encoding="utf-8"
            )
        )

        config = EVUModelConfig(
            **config_data
        )

        tokenizer = (
            ByteBPETokenizer.load(
                tokenizer_path
            )
        )

        model = EVUForCausalLM(
            config
        )

        checkpoint = torch.load(
            checkpoint_path,
            map_location=device,
            weights_only=False,
        )

        state_dict = checkpoint.get(
            "model_state_dict",
            checkpoint,
        )

        model.load_state_dict(
            state_dict
        )

        model.to(device)
        model.eval()

        return cls(
            model=model,
            tokenizer=tokenizer,
            config=config,
            checkpoint_path=checkpoint_path,
        )

    def save_config(
        self,
        path: str | Path,
    ) -> None:

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                self.config.to_dict(),
                indent=2,
            ),
            encoding="utf-8",
        )