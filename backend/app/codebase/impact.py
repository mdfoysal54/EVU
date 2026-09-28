from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .graph import CodeGraph


@dataclass
class ImpactResult:
    target: str

    direct_dependents: List[str] = field(
        default_factory=list
    )

    transitive_dependents: List[str] = field(
        default_factory=list
    )


class ImpactAnalyzer:
    def __init__(
        self,
        graph: CodeGraph,
    ) -> None:
        self.graph = graph

    def analyze(
        self,
        target: str,
        max_depth: int = 10,
    ) -> ImpactResult:
        if target not in self.graph.nodes:
            raise KeyError(
                f"Unknown graph node: {target}"
            )

        direct = [
            edge.source
            for edge in self.graph.edges
            if edge.target == target
        ]

        visited = set(direct)
        frontier = [
            (
                node,
                1,
            )
            for node in direct
        ]

        while frontier:
            current, depth = frontier.pop(0)

            if depth >= max_depth:
                continue

            parents = [
                edge.source
                for edge in self.graph.edges
                if edge.target == current
            ]

            for parent in parents:
                if parent in visited:
                    continue

                visited.add(parent)

                frontier.append(
                    (
                        parent,
                        depth + 1,
                    )
                )

        return ImpactResult(
            target=target,
            direct_dependents=direct,
            transitive_dependents=[
                node
                for node in visited
                if node not in direct
            ],
        )