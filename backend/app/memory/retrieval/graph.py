from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class GraphRetrievalResult:
    node_id: str
    score: float
    distance: int
    path: tuple[str, ...] = field(
        default_factory=tuple
    )


class GraphRetriever:
    """Graph traversal helper independent of persistence."""

    def __init__(self) -> None:
        self._adj: dict[
            str,
            set[str]
        ] = {}

        self._edge_weight: dict[
            tuple[str, str],
            float
        ] = {}

    def add_edge(
        self,
        source: str,
        target: str,
        weight: float = 1.0,
        bidirectional: bool = True,
    ) -> None:
        self._adj.setdefault(
            source,
            set(),
        ).add(target)

        self._edge_weight[
            (source, target)
        ] = float(weight)

        if bidirectional:
            self._adj.setdefault(
                target,
                set(),
            ).add(source)

            self._edge_weight[
                (target, source)
            ] = float(weight)

    def add_edges(
        self,
        edges: Iterable[
            tuple[str, str, float]
        ],
    ) -> None:
        for source, target, weight in edges:
            self.add_edge(
                source,
                target,
                weight,
            )

    def neighbors(
        self,
        node_id: str,
    ) -> set[str]:
        return set(
            self._adj.get(
                node_id,
                set(),
            )
        )

    def retrieve(
        self,
        seed_ids: Iterable[str],
        max_hops: int = 2,
        top_k: int = 10,
    ) -> list[GraphRetrievalResult]:
        if max_hops < 0 or top_k <= 0:
            return []

        seeds = list(
            dict.fromkeys(seed_ids)
        )

        frontier = [
            (
                seed,
                0,
                (seed,),
            )
            for seed in seeds
        ]

        best: dict[
            str,
            GraphRetrievalResult
        ] = {}

        visited = set(seeds)

        while frontier:
            node, distance, path = frontier.pop(0)

            if distance > 0:
                score = 1.0 / (
                    1.0 + distance
                )

                candidate = GraphRetrievalResult(
                    node,
                    score,
                    distance,
                    path,
                )

                previous = best.get(node)

                if (
                    previous is None
                    or candidate.score > previous.score
                ):
                    best[node] = candidate

            if distance >= max_hops:
                continue

            for nxt in sorted(
                self._adj.get(node, ())
            ):
                if nxt in visited:
                    continue

                visited.add(nxt)

                frontier.append(
                    (
                        nxt,
                        distance + 1,
                        path + (nxt,),
                    )
                )

        results = sorted(
            best.values(),
            key=lambda result: (
                -result.score,
                result.distance,
                result.node_id,
            ),
        )

        return results[:top_k]