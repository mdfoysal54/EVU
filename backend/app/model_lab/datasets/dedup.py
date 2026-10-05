from __future__ import annotations

import hashlib
import re
from typing import Iterable


def normalize_for_hash(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(
        r"\s+",
        " ",
        text,
    )
    return text


def fingerprint(text: str) -> str:
    normalized = normalize_for_hash(text)

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def deduplicate_records(
    records: Iterable[dict],
    *,
    key: str = "text",
) -> list[dict]:
    seen: set[str] = set()
    result: list[dict] = []

    for record in records:
        value = str(
            record.get(key, "")
        )

        digest = fingerprint(value)

        if digest in seen:
            continue

        seen.add(digest)
        result.append(record)

    return result