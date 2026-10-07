from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


class JSONLStream:
    """
    Memory-efficient JSONL reader.

    It yields one record at a time instead of loading the complete dataset
    into RAM.
    """

    def __init__(
        self,
        paths: str | Path | list[str | Path],
        *,
        text_field: str = "text",
        encoding: str = "utf-8",
    ) -> None:
        if isinstance(paths, (str, Path)):
            paths = [paths]

        self.paths = [Path(p) for p in paths]
        self.text_field = text_field
        self.encoding = encoding

    def __iter__(self) -> Iterator[dict[str, Any]]:
        for path in self.paths:
            if not path.exists():
                raise FileNotFoundError(path)

            with path.open("r", encoding=self.encoding) as handle:
                for line_number, line in enumerate(handle, start=1):
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(
                            f"Invalid JSON in {path}:{line_number}"
                        ) from exc

                    if not isinstance(record, dict):
                        continue

                    yield record

    def text_iterator(self) -> Iterator[str]:
        for record in self:
            value = record.get(self.text_field)

            if value is None:
                continue

            text = str(value).strip()

            if text:
                yield text