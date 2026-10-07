from app.model_lab.tokenization.packing import pack_token_stream
from app.model_lab.tokenization.collator import PackedCausalCollator


def test_packing():
    sequences = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8],
    ]

    packed = list(
        pack_token_stream(
            sequences,
            block_size=4,
        )
    )

    assert len(packed) == 2
    assert packed[0].input_ids == [1, 2, 3, 4]
    assert packed[1].input_ids == [5, 6, 7, 8]


def test_collator():
    collator = PackedCausalCollator(
        pad_token_id=0,
    )

    batch = collator(
        [
            {"input_ids": [1, 2, 3]},
            {"input_ids": [4, 5]},
        ]
    )

    assert batch["input_ids"].shape == (2, 3)
    assert batch["labels"].shape == (2, 3)
    assert batch["attention_mask"].shape == (2, 3)