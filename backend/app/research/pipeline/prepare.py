import json
import hashlib
from pathlib import Path

from app.research.modeling.tokenizer import (
    EVUByteTokenizer,
)


def normalize_text(
    text: str,
) -> str:

    return " ".join(
        text.strip().split()
    )


def content_hash(
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode(
            "utf-8",
            errors="replace",
        )
    ).hexdigest()


def load_jsonl(
    path: str,
) -> list[dict]:

    source = Path(path)

    if not source.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    records = []

    with source.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            records.append(
                json.loads(line)
            )

    return records


def extract_training_text(
    record: dict,
) -> str:

    messages = record.get(
        "messages",
        [],
    )

    parts = []

    for message in messages:

        role = str(
            message.get(
                "role",
                "",
            )
        )

        content = normalize_text(
            str(
                message.get(
                    "content",
                    "",
                )
            )
        )

        if not content:
            continue

        parts.append(
            f"{role}: {content}"
        )

    return "\n".join(parts)


def clean_and_deduplicate(
    records: list[dict],
) -> list[str]:

    seen = set()
    cleaned = []

    for record in records:

        text = extract_training_text(
            record
        )

        if len(text) < 10:
            continue

        digest = content_hash(text)

        if digest in seen:
            continue

        seen.add(digest)

        cleaned.append(text)

    return cleaned


def train_validation_split(
    texts: list[str],
    validation_ratio: float = 0.1,
) -> tuple[list[str], list[str]]:

    if not texts:
        return [], []

    texts = list(texts)

    split_index = max(
        1,
        int(
            len(texts)
            * (
                1
                - validation_ratio
            )
        ),
    )

    if split_index >= len(texts):
        split_index = max(
            1,
            len(texts) - 1,
        )

    return (
        texts[:split_index],
        texts[split_index:],
    )


def tokenize_texts(
    texts: list[str],
    tokenizer: EVUByteTokenizer,
) -> list[list[int]]:

    return [
        tokenizer.encode(
            text
        )
        for text in texts
    ]


def prepare_dataset(
    input_path: str,
    output_dir: str,
    validation_ratio: float = 0.1,
) -> dict:

    records = load_jsonl(
        input_path
    )

    cleaned = clean_and_deduplicate(
        records
    )

    train_texts, validation_texts = (
        train_validation_split(
            cleaned,
            validation_ratio,
        )
    )

    tokenizer = EVUByteTokenizer()

    train_tokens = tokenize_texts(
        train_texts,
        tokenizer,
    )

    validation_tokens = tokenize_texts(
        validation_texts,
        tokenizer,
    )

    output = Path(
        output_dir
    )

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    tokenizer.save(
        str(
            output
            / "tokenizer.txt"
        )
    )

    with (
        output
        / "train.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            train_tokens,
            file,
        )

    with (
        output
        / "validation.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            validation_tokens,
            file,
        )

    statistics = {
        "raw_records": len(records),
        "cleaned_unique_records": len(
            cleaned
        ),
        "train_examples": len(
            train_tokens
        ),
        "validation_examples": len(
            validation_tokens
        ),
        "vocab_size": tokenizer.vocab_size,
    }

    with (
        output
        / "statistics.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            statistics,
            file,
            indent=2,
        )

    return statistics