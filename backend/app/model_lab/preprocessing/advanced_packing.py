from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PackedSequence:
    input_ids: list[int]
    labels: list[int]
    loss_mask: list[int]


class SequencePacker:
    """
    Efficient causal-LM sequence packer.

    Multiple short documents can share one training sequence.

    The loss mask can optionally prevent loss on padding tokens.
    """

    def __init__(
        self,
        block_size: int,
        *,
        pad_token_id: int = 0,
        eos_token_id: int | None = None,
    ) -> None:
        if block_size < 2:
            raise ValueError("block_size must be >= 2")

        self.block_size = block_size
        self.pad_token_id = pad_token_id
        self.eos_token_id = eos_token_id

    def _append_document(
        self,
        stream: list[int],
        document: list[int],
    ) -> None:
        if not document:
            return

        if stream and self.eos_token_id is not None:
            stream.append(self.eos_token_id)

        stream.extend(document)

    def pack(
        self,
        sequences: list[list[int]],
        *,
        drop_remainder: bool = True,
    ) -> list[PackedSequence]:
        stream: list[int] = []

        for sequence in sequences:
            self._append_document(
                stream,
                sequence,
            )

        result: list[PackedSequence] = []

        for start in range(
            0,
            len(stream),
            self.block_size,
        ):
            chunk = stream[
                start:start + self.block_size
            ]

            if len(chunk) < self.block_size:
                if drop_remainder:
                    break

                padded = chunk + [
                    self.pad_token_id
                ] * (
                    self.block_size - len(chunk)
                )

                labels = list(padded)

                mask = [
                    1 if token != self.pad_token_id else 0
                    for token in padded
                ]
            else:
                padded = chunk
                labels = list(chunk)
                mask = [1] * self.block_size

            result.append(
                PackedSequence(
                    input_ids=padded,
                    labels=labels,
                    loss_mask=mask,
                )
            )

        return result


def shift_for_causal_lm(
    packed: PackedSequence,
) -> tuple[list[int], list[int], list[int]]:
    """
    Converts a packed sequence into:
        input_ids
        labels
        loss_mask

    where label[t] predicts input[t + 1].
    """

    input_ids = packed.input_ids[:-1]
    labels = packed.labels[1:]
    loss_mask = packed.loss_mask[1:]

    return input_ids, labels, loss_mask