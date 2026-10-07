from .config import LoRAConfig
from .layer import LoRALinear
from .inject import inject_lora, trainable_parameters
from .state import save_lora_adapter, load_lora_adapter
from .trainer import LoRATrainer
from .qlora import QLoRAConfig, prepare_qlora_model

# Check if trainable_parameter_count exists in inject, otherwise alias trainable_parameters
try:
    from .inject import trainable_parameter_count
except ImportError:
    # If trainable_parameters returns an iterable/generator of parameters, count them;
    # if it already returns an integer count, alias directly.
    def trainable_parameter_count(model):
        res = trainable_parameters(model)
        if isinstance(res, (int, float)):
            return int(res)
        return sum(p.numel() for p in res if hasattr(p, "numel"))

__all__ = [
    "LoRAConfig",
    "LoRALinear",
    "inject_lora",
    "trainable_parameters",
    "trainable_parameter_count",
    "save_lora_adapter",
    "load_lora_adapter",
    "LoRATrainer",
    "QLoRAConfig",
    "prepare_qlora_model",
]