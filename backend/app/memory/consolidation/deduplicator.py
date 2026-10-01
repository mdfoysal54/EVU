from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable


@dataclass(frozen=True)
class DuplicateGroup:
    canonical_id: str
    duplicate_ids: tuple[str, ...]
    similarity: float


def normalize_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        (text or "").strip().lower(),
    )


class MemoryDeduplicator:
    def __init__(
        self,
        threshold: float = 0.92,
    ) -> None:
        if not 0 <= threshold <= 1:
            raise ValueError(
                "threshold must be between 0 and 1"
            )

        self.threshold = threshold

    def similarity(
        self,
        a: str,
        b: str,
    ) -> float:
        na = normalize_text(a)
        nb = normalize_text(b)

        if not na or not nb:
            return 0.0

        if na == nb:
            return 1.0

        return SequenceMatcher(
            None,
            na,
            nb,
            autojunk=False,
        ).ratio()

    def find_groups(
        self,
        items: Iterable[
            tuple[str, str]
        ],
    ) -> list[DuplicateGroup]:
        data = list(items)

        groups = []
        consumed: set[str] = set()

        for i, (item_id, text) in enumerate(
            data
        ):
            if item_id in consumed:
                continue

            duplicates = []
            best_similarity = 0.0

            for other_id, other_text in data[
                i + 1:
            ]:
                if other_id in consumed:
                    continue

                similarity = self.similarity(
                    text,
                    other_text,
                )

                if (
                    similarity
                    >= self.threshold
                ):
                    duplicates.append(
                        other_id
                    )

                    best_similarity = max(
                        best_similarity,
                        similarity,
                    )

                    consumed.add(
                        other_id
                    )

            if duplicates:
                groups.append(
                    DuplicateGroup(
                        canonical_id=item_id,
                        duplicate_ids=tuple(
                            duplicates
                        ),
                        similarity=best_similarity,
                    )
                )

        return groups