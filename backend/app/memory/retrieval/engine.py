from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from .bm25 import BM25Index
from .graph import GraphRetriever
from .vector import VectorIndex


@dataclass(frozen=True)
class RetrievalHit:
    memory_id: str
    score: float
    channels: dict[str, float] = field(
        default_factory=dict
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class RetrievalWeights:
    lexical: float = 0.35
    vector: float = 0.45
    graph: float = 0.20

    def normalize(self) -> "RetrievalWeights":
        total = (
            self.lexical
            + self.vector
            + self.graph
        )

        if total <= 0:
            raise ValueError(
                "At least one retrieval weight must be positive"
            )

        self.lexical /= total
        self.vector /= total
        self.graph /= total

        return self


class MemoryRetrievalEngine:
    """Hybrid EVU memory retrieval engine."""

    def __init__(
        self,
        bm25: BM25Index | None = None,
        vector: VectorIndex | None = None,
        graph: GraphRetriever | None = None,
        weights: RetrievalWeights | None = None,
    ) -> None:
        self.bm25 = bm25 or BM25Index()
        self.vector = vector
        self.graph = graph or GraphRetriever()

        self.weights = (
            weights or RetrievalWeights()
        ).normalize()

    @staticmethod
    def _normalize(
        values: dict[str, float],
    ) -> dict[str, float]:
        if not values:
            return {}

        lo = min(values.values())
        hi = max(values.values())

        if hi == lo:
            return {
                key: (
                    1.0
                    if hi > 0
                    else 0.0
                )
                for key in values
            }

        return {
            key: (value - lo) / (hi - lo)
            for key, value in values.items()
        }

    def index(
        self,
        memory_id: str,
        text: str,
        vector: Sequence[float] | None = None,
    ) -> None:
        self.bm25.add(
            memory_id,
            text,
        )

        if self.vector is not None:
            self.vector.add(
                memory_id,
                text,
                vector,
            )

    def remove(
        self,
        memory_id: str,
    ) -> None:
        self.bm25.remove(memory_id)

        if self.vector is not None:
            self.vector.remove(memory_id)

    def search(
        self,
        query: str,
        *,
        top_k: int = 10,
        vector: Sequence[float] | None = None,
        graph_seed_ids: Sequence[str] | None = None,
        graph_hops: int = 2,
    ) -> list[RetrievalHit]:
        if top_k <= 0:
            return []

        channel: dict[
            str,
            dict[str, float]
        ] = {
            "lexical": {},
            "vector": {},
            "graph": {},
        }

        for hit in self.bm25.search(
            query,
            max(top_k * 3, 20),
        ):
            channel["lexical"][
                hit.doc_id
            ] = hit.score

        if self.vector is not None:
            if vector is not None:
                vector_hits = (
                    self.vector.search_vector(
                        vector,
                        max(top_k * 3, 20),
                    )
                )
            else:
                vector_hits = (
                    self.vector.search(
                        query,
                        max(top_k * 3, 20),
                    )
                )

            channel["vector"] = {
                hit.doc_id: hit.score
                for hit in vector_hits
            }

        if graph_seed_ids:
            channel["graph"] = {
                hit.node_id: hit.score
                for hit in self.graph.retrieve(
                    graph_seed_ids,
                    graph_hops,
                    max(top_k * 3, 20),
                )
            }

        normalized = {
            name: self._normalize(scores)
            for name, scores in channel.items()
        }

        ids = set().union(
            *[
                set(values)
                for values in normalized.values()
            ]
        )

        hits: list[RetrievalHit] = []

        for memory_id in ids:
            channels = {
                name: normalized[name].get(
                    memory_id,
                    0.0,
                )
                for name in normalized
            }

            score = (
                self.weights.lexical
                * channels["lexical"]
                + self.weights.vector
                * channels["vector"]
                + self.weights.graph
                * channels["graph"]
            )

            hits.append(
                RetrievalHit(
                    memory_id,
                    score,
                    channels,
                )
            )

        hits.sort(
            key=lambda hit: (
                -hit.score,
                hit.memory_id,
            )
        )

        return hits[:top_k]