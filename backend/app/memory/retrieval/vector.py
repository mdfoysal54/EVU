from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence


@dataclass(frozen=True)
class VectorResult:
    doc_id: str
    score: float


def cosine_similarity(
    a: Sequence[float],
    b: Sequence[float],
) -> float:
    if len(a) != len(b):
        raise ValueError(
            "Vectors must have the same dimension"
        )

    dot = sum(
        x * y
        for x, y in zip(a, b)
    )

    na = math.sqrt(
        sum(x * x for x in a)
    )

    nb = math.sqrt(
        sum(y * y for y in b)
    )

    if na == 0 or nb == 0:
        return 0.0

    return dot / (na * nb)


class VectorIndex:
    """Provider-independent in-memory vector index."""

    def __init__(
        self,
        embedder: Callable[
            [str],
            Sequence[float]
        ] | None = None,
    ) -> None:
        self.embedder = embedder
        self._vectors: dict[
            str,
            tuple[float, ...]
        ] = {}

        self._texts: dict[str, str] = {}

    def add(
        self,
        doc_id: str,
        text: str,
        vector: Sequence[float] | None = None,
    ) -> None:
        if vector is None:
            if self.embedder is None:
                raise ValueError(
                    "No vector supplied and no embedder configured"
                )

            vector = self.embedder(text)

        values = tuple(
            float(value)
            for value in vector
        )

        if not values:
            raise ValueError(
                "Vector cannot be empty"
            )

        self._vectors[doc_id] = values
        self._texts[doc_id] = text

    def add_many(
        self,
        documents: Iterable[
            tuple[
                str,
                str,
                Sequence[float] | None,
            ]
        ],
    ) -> None:
        for doc_id, text, vector in documents:
            self.add(
                doc_id,
                text,
                vector,
            )

    def remove(self, doc_id: str) -> bool:
        existed = doc_id in self._vectors

        self._vectors.pop(doc_id, None)
        self._texts.pop(doc_id, None)

        return existed

    def clear(self) -> None:
        self._vectors.clear()
        self._texts.clear()

    def search_vector(
        self,
        query_vector: Sequence[float],
        top_k: int = 10,
        min_score: float = -1.0,
    ) -> list[VectorResult]:
        if top_k <= 0:
            return []

        scored = []

        for doc_id, vector in self._vectors.items():
            score = cosine_similarity(
                query_vector,
                vector,
            )

            if score >= min_score:
                scored.append(
                    VectorResult(
                        doc_id,
                        score,
                    )
                )

        scored.sort(
            key=lambda result: (
                -result.score,
                result.doc_id,
            )
        )

        return scored[:top_k]

    def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = -1.0,
    ) -> list[VectorResult]:
        if self.embedder is None:
            raise ValueError(
                "No embedder configured"
            )

        return self.search_vector(
            self.embedder(query),
            top_k,
            min_score,
        )

    def get(
        self,
        doc_id: str,
    ) -> tuple[float, ...] | None:
        return self._vectors.get(doc_id)