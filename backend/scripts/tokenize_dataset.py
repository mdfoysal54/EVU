from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.model_lab.preprocessing.advanced_packing import (
    SequencePacker,
)
from app.model_lab.tokenizer.advanced import (
    AdvancedTokenizer,
)
from app.model_lab.tokenizer.byte_bpe import (
    ByteBPETokenizer,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
    )

    parser.add_argument(
        "--tokenizer",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--block-size",
        type=int,
        default=512,
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=None,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    tokenizer = ByteBPETokenizer.load(
        args.tokenizer
    )

    advanced = AdvancedTokenizer(tokenizer)

    texts: list[str] = []

    with open(
        args.input,
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            record = json.loads(line)

            text = str(
                record.get("text", "")
            ).strip()

            if text:
                texts.append(text)

    sequences, stats = advanced.encode_batch(
        texts,
        max_length=args.max_length,
    )

    packer = SequencePacker(
        args.block_size,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )

    packed = packer.pack(
        sequences,
        drop_remainder=True,
    )

    output = Path(args.output)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for item in packed:
            handle.write(
                json.dumps(
                    {
                        "input_ids": item.input_ids,
                        "labels": item.labels,
                        "loss_mask": item.loss_mask,
                    }
                )
                + "\n"
            )

    print("TOKENIZATION COMPLETE")
    print("documents:", stats.documents)
    print("tokens:", stats.tokens)
    print("truncated:", stats.truncated_documents)
    print("packed_sequences:", len(packed))


if __name__ == "__main__":
    main()