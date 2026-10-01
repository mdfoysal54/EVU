from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

_TOKEN_RE = re.compile(r"[\w']+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


@dataclass(frozen=True)
class BM25Result:
    doc_id: str
    score: float


class BM25Index:
    """Small in-process BM25 index suitable for EVU's memory layer."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        if k1 < 0 or not 0 <= b <= 1:
            raise ValueError("BM25 requires k1 >= 0 and 0 <= b <= 1")

        self.k1 = k1
        self.b = b
        self._docs: dict[str, str] = {}
        self._tf: dict[str, Counter[str]] = {}
        self._df: Counter[str] = Counter()
        self._lengths: dict[str, int] = {}
        self._avgdl = 0.0

    def add(self, doc_id: str, text: str) -> None:
        if doc_id in self._docs:
            self.remove(doc_id)

        tokens = tokenize(text)
        tf = Counter(tokens)

        self._docs[doc_id] = text
        self._tf[doc_id] = tf
        self._lengths[doc_id] = len(tokens)

        for term in tf:
            self._df[term] += 1

        self._refresh_avgdl()

    def add_many(self, documents: Iterable[tuple[str, str]]) -> None:
        for doc_id, text in documents:
            self.add(doc_id, text)

    def remove(self, doc_id: str) -> bool:
        tf = self._tf.pop(doc_id, None)

        self._docs.pop(doc_id, None)
        self._lengths.pop(doc_id, None)

        if tf is None:
            return False

        for term in tf:
            self._df[term] -= 1

            if self._df[term] <= 0:
                del self._df[term]

        self._refresh_avgdl()
        return True

    def clear(self) -> None:
        self._docs.clear()
        self._tf.clear()
        self._df.clear()
        self._lengths.clear()
        self._avgdl = 0.0

    def _refresh_avgdl(self) -> None:
        self._avgdl = (
            sum(self._lengths.values()) / len(self._lengths)
            if self._lengths
            else 0.0
        )

    def _idf(self, term: str) -> float:
        n = len(self._docs)
        df = self._df.get(term, 0)

        if not n or not df:
            return 0.0

        return math.log(
            1.0 + (n - df + 0.5) / (df + 0.5)
        )

    def score(self, query: str, doc_id: str) -> float:
        if doc_id not in self._docs:
            return 0.0

        terms = tokenize(query)

        if not terms or not self._avgdl:
            return 0.0

        tf = self._tf[doc_id]
        dl = self._lengths[doc_id]

        score = 0.0

        for term in terms:
            freq = tf.get(term, 0)

            if not freq:
                continue

            idf = self._idf(term)

            denom = (
                freq
                + self.k1
                * (
                    1
                    - self.b
                    + self.b * dl / self._avgdl
                )
            )

            score += (
                idf
                * (freq * (self.k1 + 1))
                / denom
            )

        return score

    def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> list[BM25Result]:
        if top_k <= 0:
            return []

        scored = [
            BM25Result(
                doc_id,
                self.score(query, doc_id),
            )
            for doc_id in self._docs
        ]

        scored = [
            result
            for result in scored
            if result.score >= min_score
        ]

        scored.sort(
            key=lambda result: (
                -result.score,
                result.doc_id,
            )
        )

        return scored[:top_k]

    def documents(self) -> Sequence[str]:
        return tuple(self._docs.keys())