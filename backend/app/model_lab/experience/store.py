from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .schema import ExperienceRecord


class ExperienceStore:
    """
    Persistent append-only JSONL store for EVU experiences.

    JSONL is used for Block 5 because it is:

    - simple
    - append friendly
    - easy to inspect
    - easy to convert into datasets
    - compatible with future distributed storage
    """

    def __init__(
        self,
        path: str | Path = "./data/experience/experiences.jsonl",
    ) -> None:

        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def append(
        self,
        experience: ExperienceRecord,
    ) -> None:

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                json.dumps(
                    experience.to_dict(),
                    ensure_ascii=False,
                )
            )

            handle.write("\n")

    def append_many(
        self,
        experiences: Iterable[ExperienceRecord],
    ) -> None:

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as handle:

            for experience in experiences:
                handle.write(
                    json.dumps(
                        experience.to_dict(),
                        ensure_ascii=False,
                    )
                )

                handle.write("\n")

    def load_all(
        self,
    ) -> list[ExperienceRecord]:

        if not self.path.exists():
            return []

        records: list[ExperienceRecord] = []

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as handle:

            for line in handle:
                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)

                records.append(
                    ExperienceRecord.from_dict(
                        data
                    )
                )

        return records

    def count(self) -> int:
        if not self.path.exists():
            return 0

        count = 0

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as handle:

            for line in handle:
                if line.strip():
                    count += 1

        return count

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()