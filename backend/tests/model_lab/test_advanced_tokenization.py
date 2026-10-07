from app.model_lab.preprocessing.advanced_packing import (
    SequencePacker,
    shift_for_causal_lm,
)


def test_sequence_packing():
    packer = SequencePacker(
        block_size=8,
        pad_token_id=0,
        eos_token_id=2,
    )

    sequences = [
        [10, 11, 12],
        [13, 14],
        [15, 16, 17],
    ]

    packed = packer.pack(
        sequences,
        drop_remainder=False,
    )

    assert packed
    assert len(packed[0].input_ids) == 8


def test_causal_shift():
    packer = SequencePacker(
        block_size=4,
        pad_token_id=0,
    )

    packed = packer.pack(
        [[1, 2, 3, 4]],
        drop_remainder=True,
    )[0]

    input_ids, labels, mask = shift_for_causal_lm(
        packed
    )

    assert input_ids == [1, 2, 3]
    assert labels == [2, 3, 4]
    assert mask == [1, 1, 1]