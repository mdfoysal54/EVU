from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DatasetRecord:
    text: str
    source: str = "unknown"
    license: str | None = None
    language: str | None = None
    record_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DatasetStats:
    input_records: int = 0
    accepted_records: int = 0
    rejected_records: int = 0
    duplicate_records: int = 0
    train_records: int = 0
    validation_records: int = 0
    output_tokens: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)