"""
EVU Model Lab fine-tuning package.
"""

from .adapters import (
    LoRALinear,
    freeze_model,
    trainable_parameters,
)

from .sft import (
    SFTExample,
    SFTDataset,
)

from .preference import (
    PreferenceExample,
    PreferenceDataset,
    TokenizedPreferenceExample,
    dpo_loss,
)

__all__ = [
    "LoRALinear",
    "freeze_model",
    "trainable_parameters",
    "SFTExample",
    "SFTDataset",
    "PreferenceExample",
    "PreferenceDataset",
    "TokenizedPreferenceExample",
    "dpo_loss",
]