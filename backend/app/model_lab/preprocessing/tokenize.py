from __future__ import annotations

from collections.abc import Iterable


def tokenize_records(records: Iterable[dict], tokenizer, text_field: str = "text") -> list[list[int]]:
    return [tokenizer.encode(str(record[text_field])) for record in records if record.get(text_field)]