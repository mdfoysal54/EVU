from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set

from .graph import CodeGraph


@dataclass
class TraceResult:
    start: str
    direction: str
    nodes: List[str] = field(
        default_factory=list
    )
    relations: List[str] = field(
        default_factory=list
    )


class CodeTracer:
    def __init__(
        self,
        graph: CodeGraph,
    ) -> None:
        self.graph = graph

    def trace(
        self,
        start_node: str,
        direction: str = "out",
        max_depth: int = 5,
    ) -> TraceResult:
        if start_node not in self.graph.nodes:
            raise KeyError(
                f"Unknown graph node: {start_node}"
            )

        visited: Set[str] = {
            start_node
        }

        nodes: list[str] = []
        relations: list[str] = []

        frontier = [
            (
                start_node,
                0,
            )
        ]

        while frontier:
            current, depth = frontier.pop(0)

            if depth >= max_depth:
                continue

            edges = [
                edge
                for edge in self.graph.edges
                if (
                    edge.source == current
                    if direction == "out"
                    else edge.target == current
                )
            ]

            for edge in edges:
                next_node = (
                    edge.target
                    if direction == "out"
                    else edge.source
                )

                if next_node in visited:
                    continue

                visited.add(next_node)

                nodes.append(next_node)
                relations.append(edge.relation)

                frontier.append(
                    (
                        next_node,
                        depth + 1,
                    )
                )

        return TraceResult(
            start=start_node,
            direction=direction,
            nodes=nodes,
            relations=relations,
        )