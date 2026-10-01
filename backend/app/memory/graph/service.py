from __future__ import annotations

from collections import defaultdict
from threading import RLock

from .extractor import (
    ExtractionResult,
    MemoryGraphExtractor,
)
from .models import MemoryEdge, MemoryNode


class MemoryGraphService:
    """Thread-safe graph service.

    Persistence can later be backed by PostgreSQL, Neo4j, etc.
    """

    def __init__(
        self,
        extractor: MemoryGraphExtractor | None = None,
    ) -> None:
        self.extractor = (
            extractor
            or MemoryGraphExtractor()
        )

        self._nodes: dict[
            str,
            MemoryNode
        ] = {}

        self._edges: dict[
            str,
            MemoryEdge
        ] = {}

        self._out: dict[
            str,
            set[str]
        ] = defaultdict(set)

        self._in: dict[
            str,
            set[str]
        ] = defaultdict(set)

        self._lock = RLock()

    def upsert_node(
        self,
        node: MemoryNode,
    ) -> MemoryNode:
        with self._lock:
            existing = self._nodes.get(
                node.id
            )

            if existing:
                existing.kind = node.kind
                existing.label = node.label
                existing.content = node.content
                existing.properties.update(
                    node.properties
                )
                existing.confidence = max(
                    existing.confidence,
                    node.confidence,
                )
                existing.touch()

                return existing

            self._nodes[node.id] = node

            return node

    def add_edge(
        self,
        edge: MemoryEdge,
    ) -> MemoryEdge:
        if (
            edge.source not in self._nodes
            or edge.target not in self._nodes
        ):
            raise KeyError(
                "Both edge endpoints must exist"
            )

        with self._lock:
            self._edges[edge.id] = edge

            self._out[
                edge.source
            ].add(edge.id)

            self._in[
                edge.target
            ].add(edge.id)

            return edge

    def ingest(
        self,
        text: str,
        source_memory_id: str | None = None,
    ) -> ExtractionResult:
        result = self.extractor.extract(
            text,
            source_memory_id,
        )

        with self._lock:
            for node in result.nodes:
                self.upsert_node(node)

            for edge in result.edges:
                if (
                    edge.source in self._nodes
                    and edge.target in self._nodes
                ):
                    self.add_edge(edge)

        return result

    def get_node(
        self,
        node_id: str,
    ) -> MemoryNode | None:
        return self._nodes.get(node_id)

    def neighbors(
        self,
        node_id: str,
        relation: str | None = None,
    ) -> list[MemoryNode]:
        result = []

        for edge_id in self._out.get(
            node_id,
            set(),
        ):
            edge = self._edges[edge_id]

            if (
                relation is not None
                and edge.relation != relation
            ):
                continue

            node = self._nodes.get(
                edge.target
            )

            if node:
                result.append(node)

        return result

    def related(
        self,
        node_id: str,
        max_hops: int = 2,
    ) -> list[MemoryNode]:
        seen = {node_id}

        queue = [
            (
                node_id,
                0,
            )
        ]

        result = []

        while queue:
            current, distance = queue.pop(0)

            if distance >= max_hops:
                continue

            for node in self.neighbors(
                current
            ):
                if node.id in seen:
                    continue

                seen.add(node.id)

                result.append(node)

                queue.append(
                    (
                        node.id,
                        distance + 1,
                    )
                )

        return result

    def all_nodes(self) -> list[MemoryNode]:
        return list(
            self._nodes.values()
        )

    def all_edges(self) -> list[MemoryEdge]:
        return list(
            self._edges.values()
        )