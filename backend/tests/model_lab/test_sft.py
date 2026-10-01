import torch

from app.model_lab.architecture.config import (
    EVUModelConfig,
)

from app.model_lab.architecture.model import (
    EVUForCausalLM,
)

from app.model_lab.sft.dataset import (
    SFTCollator,
    SFTDataset,
)

from app.model_lab.sft.schema import (
    ConversationExample,
    Message,
)

from app.model_lab.sft.split import (
    split_examples,
)


def build_tokenizer():

    from app.model_lab.tokenizer.byte_bpe import (
        ByteBPETokenizer,
    )

    tokenizer = ByteBPETokenizer()

    tokenizer.train(
        [
            "System: You are EVU.",
            "User: Hello",
            "Assistant: Hello, how can I help?",
            "User: What is Python?",
            "Assistant: Python is a programming language.",
        ]
    )

    return tokenizer


def build_example():

    return ConversationExample(
        messages=[
            Message(
                role="system",
                content="You are EVU.",
            ),
            Message(
                role="user",
                content="Hello",
            ),
            Message(
                role="assistant",
                content=(
                    "Hello, how can I help?"
                ),
            ),
        ]
    )


def test_sft_dataset_masks_prompt():

    tokenizer = build_tokenizer()

    dataset = SFTDataset(
        [build_example()],
        tokenizer,
        max_length=128,
    )

    item = dataset[0]

    assert (
        len(item.input_ids)
        == len(item.labels)
    )

    assert -100 in item.labels

    assert any(
        token != -100
        for token in item.labels
    )


def test_sft_collator():

    tokenizer = build_tokenizer()

    dataset = SFTDataset(
        [
            build_example(),
            build_example(),
        ],
        tokenizer,
        max_length=128,
    )

    batch = SFTCollator(
        tokenizer.pad_token_id
    )(
        [
            dataset[0],
            dataset[1],
        ]
    )

    assert batch.input_ids.ndim == 2

    assert (
        batch.labels.shape
        == batch.input_ids.shape
    )

    assert (
        batch.attention_mask.shape
        == batch.input_ids.shape
    )


def test_split():

    examples = [
        build_example()
        for _ in range(10)
    ]

    train, validation = (
        split_examples(
            examples,
            validation_fraction=0.2,
            seed=42,
        )
    )

    assert len(train) == 8
    assert len(validation) == 2


def test_model_sft_forward():

    tokenizer = build_tokenizer()

    dataset = SFTDataset(
        [build_example()],
        tokenizer,
        max_length=128,
    )

    batch = SFTCollator(
        tokenizer.pad_token_id
    )(
        [dataset[0]]
    )

    config = EVUModelConfig.tiny(
        vocab_size=len(tokenizer)
    )

    model = EVUForCausalLM(
        config
    )

    result = model(
        input_ids=batch.input_ids,
        labels=batch.labels,
        attention_mask=batch.attention_mask,
    )

    assert result.loss is not None

    assert torch.isfinite(
        result.loss
    )