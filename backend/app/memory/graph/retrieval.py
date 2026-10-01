from __future__ import annotations

from dataclasses import dataclass

from .service import MemoryGraphService


@dataclass(frozen=True)
class GraphMemoryHit:
    node_id: str
    label: str
    relation_path: tuple[str, ...]
    score: float


class MemoryGraphRetriever:
    def __init__(
        self,
        graph: MemoryGraphService,
    ) -> None:
        self.graph = graph

    def retrieve(
        self,
        seed_ids: list[str],
        max_hops: int = 2,
        top_k: int = 10,
    ) -> list[GraphMemoryHit]:
        if top_k <= 0:
            return []

        hits: dict[
            str,
            GraphMemoryHit
        ] = {}

        for seed in seed_ids:
            frontier = [
                (
                    seed,
                    (seed,),
                    0,
                )
            ]

            visited = {seed}

            while frontier:
                (
                    node_id,
                    path,
                    distance,
                ) = frontier.pop(0)

                if distance > 0:
                    node = self.graph.get_node(
                        node_id
                    )

                    if node:
                        hit = GraphMemoryHit(
                            node_id,
                            node.label,
                            path,
                            1.0 / (
                                1 + distance
                            ),
                        )

                        if (
                            node_id not in hits
                            or hit.score
                            > hits[node_id].score
                        ):
                            hits[node_id] = hit

                if distance >= max_hops:
                    continue

                for node in self.graph.neighbors(
                    node_id
                ):
                    if node.id in visited:
                        continue

                    visited.add(node.id)

                    frontier.append(
                        (
                            node.id,
                            path + (node.id,),
                            distance + 1,
                        )
                    )

        return sorted(
            hits.values(),
            key=lambda hit: (
                -hit.score,
                hit.node_id,
            ),
        )[:top_k]