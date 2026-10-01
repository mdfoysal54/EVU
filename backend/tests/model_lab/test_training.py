import torch
from torch.utils.data import DataLoader

from app.model_lab.architecture import EVUModelConfig, EVUTransformer
from app.model_lab.training import (
    TokenSequence,
    LanguageModelDataset,
    CausalBatchCollator,
    TrainingConfig,
    Trainer,
    create_optimizer,
)


def test_one_training_epoch():
    config = EVUModelConfig.tiny(vocab_size=64)
    model = EVUTransformer(config)
    dataset = LanguageModelDataset([
        TokenSequence(list(range(16)), list(range(16))),
        TokenSequence(list(range(16)), list(range(16))),
    ])
    loader = DataLoader(
        dataset,
        batch_size=2,
        collate_fn=CausalBatchCollator(pad_token_id=0),
    )
    optimizer = create_optimizer(model)
    trainer = Trainer(
        model,
        optimizer,
        config=TrainingConfig(epochs=1, device="cpu"),
    )
    result = trainer.fit(loader)
    assert result.global_step == 1
    assert result.average_loss > 0