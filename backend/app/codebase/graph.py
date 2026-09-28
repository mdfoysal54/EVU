from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GraphNode:
    node_id: str
    node_type: str
    name: str
    metadata: Dict[str, object] = field(
        default_factory=dict
    )


@dataclass
class GraphEdge:
    source: str
    target: str
    relation: str
    metadata: Dict[str, object] = field(
        default_factory=dict
    )


class CodeGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_node(
        self,
        node: GraphNode,
    ) -> None:
        self.nodes[node.node_id] = node

    def add_edge(
        self,
        edge: GraphEdge,
    ) -> None:
        if edge.source not in self.nodes:
            raise KeyError(
                f"Unknown source node: {edge.source}"
            )

        if edge.target not in self.nodes:
            raise KeyError(
                f"Unknown target node: {edge.target}"
            )

        self.edges.append(edge)

    def neighbors(
        self,
        node_id: str,
        relation: Optional[str] = None,
    ) -> List[GraphNode]:
        target_ids = []

        for edge in self.edges:
            if edge.source != node_id:
                continue

            if (
                relation is not None
                and edge.relation != relation
            ):
                continue

            target_ids.append(edge.target)

        return [
            self.nodes[node_id]
            for node_id in target_ids
            if node_id in self.nodes
        ]

    def predecessors(
        self,
        node_id: str,
        relation: Optional[str] = None,
    ) -> List[GraphNode]:
        source_ids = []

        for edge in self.edges:
            if edge.target != node_id:
                continue

            if (
                relation is not None
                and edge.relation != relation
            ):
                continue

            source_ids.append(edge.source)

        return [
            self.nodes[node_id]
            for node_id in source_ids
            if node_id in self.nodes
        ]

    def find_node(
        self,
        name: str,
    ) -> Optional[GraphNode]:
        for node in self.nodes.values():
            if node.name == name:
                return node

        return None