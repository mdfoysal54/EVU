"""
EVU Model Lab training package.
"""

from .dataset import (
    TokenSequence,
    LanguageModelDataset,
    TextDataset,
)

from .batching import (
    Batch,
    CausalBatchCollator,
)

from .loss import (
    causal_language_model_loss,
)

from .optimizer import (
    OptimizerConfig,
    create_optimizer,
)

from .scheduler import (
    create_cosine_scheduler,
)

from .checkpoint import (
    CheckpointManager,
    CheckpointState,
)

from .trainer import (
    Trainer,
    TrainingConfig,
    TrainingResult,
)

__all__ = [
    "TokenSequence",
    "LanguageModelDataset",
    "TextDataset",
    "Batch",
    "CausalBatchCollator",
    "causal_language_model_loss",
    "OptimizerConfig",
    "create_optimizer",
    "create_cosine_scheduler",
    "CheckpointManager",
    "CheckpointState",
    "Trainer",
    "TrainingConfig",
    "TrainingResult",
]