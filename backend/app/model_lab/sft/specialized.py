from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class SpecializedExample:
    prompt: str
    response: str
    task_type: str
    metadata: dict


def normalize_example(
    record: dict,
    task_type: str,
) -> SpecializedExample:
    prompt = str(
        record.get("prompt")
        or record.get("instruction")
        or record.get("input")
        or ""
    )

    response = str(
        record.get("response")
        or record.get("output")
        or record.get("answer")
        or ""
    )

    return SpecializedExample(
        prompt=prompt.strip(),
        response=response.strip(),
        task_type=task_type,
        metadata=dict(
            record.get("metadata", {})
        ),
    )


def load_specialized_records(
    records: Iterable[dict],
    task_type: str,
) -> list[SpecializedExample]:
    result = []

    for record in records:
        example = normalize_example(
            record,
            task_type,
        )

        if not example.prompt:
            continue

        if not example.response:
            continue

        result.append(example)

    return result