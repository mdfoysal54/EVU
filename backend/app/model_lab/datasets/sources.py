from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Iterable, Iterator


@dataclass
class TextRecord:
    text: str
    source: str = ""
    record_id: str = ""
    language: str = ""
    metadata: dict = None

    def to_dict(self) -> dict:
        return {**asdict(self), "metadata": self.metadata or {}}


def load_text_file(path: str | Path) -> Iterator[TextRecord]:
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    yield TextRecord(text=text, source=str(path), record_id=path.name)


def load_jsonl(path: str | Path, text_field: str = "text") -> Iterator[TextRecord]:
    path = Path(path)
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            obj = json.loads(line)
            text = str(obj.get(text_field, ""))
            yield TextRecord(
                text=text,
                source=str(path),
                record_id=str(obj.get("id", f"{path.name}:{line_no}")),
                language=str(obj.get("language", "")),
                metadata=obj,
            )


def iter_records(paths: Iterable[str | Path]) -> Iterator[TextRecord]:
    for raw in paths:
        path = Path(raw)
        if path.suffix.lower() == ".jsonl":
            yield from load_jsonl(path)
        else:
            yield from load_text_file(path)