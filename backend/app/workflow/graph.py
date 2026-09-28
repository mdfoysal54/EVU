from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set

from .models import EdgeSpec, NodeSpec


class GraphError(Exception):
    pass


@dataclass
class WorkflowGraph:
    nodes: Dict[str, NodeSpec]
    edges: List[EdgeSpec]

    def __init__(
        self,
        nodes: Iterable[NodeSpec] = (),
        edges: Iterable[EdgeSpec] = (),
    ) -> None:

        self.nodes = {}
        self.edges = list(edges)

        for node in nodes:
            self.add_node(node)

        self.validate()

    def add_node(self, node: NodeSpec) -> None:
        if node.id in self.nodes:
            raise GraphError(
                f"Duplicate workflow node: {node.id}"
            )

        self.nodes[node.id] = node

    def add_edge(self, edge: EdgeSpec) -> None:
        if edge.source not in self.nodes:
            raise GraphError(
                f"Unknown source node: {edge.source}"
            )

        if edge.target not in self.nodes:
            raise GraphError(
                f"Unknown target node: {edge.target}"
            )

        self.edges.append(edge)
        self.validate()

    def outgoing(self, node_id: str) -> List[EdgeSpec]:
        return [
            edge
            for edge in self.edges
            if edge.source == node_id
        ]

    def incoming(self, node_id: str) -> List[EdgeSpec]:
        return [
            edge
            for edge in self.edges
            if edge.target == node_id
        ]

    def dependencies(self, node_id: str) -> Set[str]:
        return {
            edge.source
            for edge in self.incoming(node_id)
        }

    def roots(self) -> List[str]:
        return [
            node_id
            for node_id in self.nodes
            if not self.incoming(node_id)
        ]

    def leaves(self) -> List[str]:
        return [
            node_id
            for node_id in self.nodes
            if not self.outgoing(node_id)
        ]

    def topological_order(self) -> List[str]:
        indegree = {
            node_id: len(self.incoming(node_id))
            for node_id in self.nodes
        }

        queue = deque(
            node_id
            for node_id, degree in indegree.items()
            if degree == 0
        )

        result: List[str] = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for edge in self.outgoing(current):
                indegree[edge.target] -= 1

                if indegree[edge.target] == 0:
                    queue.append(edge.target)

        if len(result) != len(self.nodes):
            raise GraphError(
                "Workflow graph contains a cycle."
            )

        return result

    def validate(self) -> None:
        for edge in self.edges:
            if edge.source not in self.nodes:
                raise GraphError(
                    f"Unknown edge source: {edge.source}"
                )

            if edge.target not in self.nodes:
                raise GraphError(
                    f"Unknown edge target: {edge.target}"
                )

        self.topological_order()