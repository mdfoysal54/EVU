from __future__ import annotations

from collections import defaultdict, deque

from ..ir import DiagramIR
from .base import (
    LayoutEngine,
    LayoutResult,
    NodePosition,
    Point,
    estimate_node_size,
)


class GraphLayout(LayoutEngine):
    """
    Generic graph layout using breadth-first levels.

    This is not intended to compete with a full force-directed graph
    library. It provides a deterministic layout that works without
    external dependencies.
    """

    name = "graph"

    def layout(
        self,
        diagram: DiagramIR,
        *,
        horizontal_gap: float = 80,
        vertical_gap: float = 100,
        margin: float = 40,
        **kwargs,
    ) -> LayoutResult:

        if not diagram.nodes:
            return LayoutResult(0, 0)

        adjacency: dict[str, list[str]] = defaultdict(list)
        incoming: dict[str, int] = {
            node.id: 0
            for node in diagram.nodes
        }

        for edge in diagram.edges:
            adjacency[edge.source].append(edge.target)

            if edge.target in incoming:
                incoming[edge.target] += 1

        roots = [
            node.id
            for node in diagram.nodes
            if incoming[node.id] == 0
        ]

        if not roots:
            roots = [diagram.nodes[0].id]

        levels: dict[str, int] = {}
        queue = deque()

        for root in roots:
            levels[root] = 0
            queue.append(root)

        while queue:
            current = queue.popleft()

            for child in adjacency[current]:
                proposed = levels[current] + 1

                if (
                    child not in levels
                    or proposed > levels[child]
                ):
                    levels[child] = proposed

                if child not in queue:
                    queue.append(child)

        for node in diagram.nodes:
            levels.setdefault(node.id, 0)

        grouped: dict[int, list[str]] = defaultdict(list)

        for node_id, level in levels.items():
            grouped[level].append(node_id)

        positions: dict[str, NodePosition] = {}

        max_width = 0
        max_height = 0

        for level, node_ids in grouped.items():
            y = margin + level * (80 + vertical_gap)

            x = margin

            for node_id in node_ids:
                node = diagram.get_node(node_id)

                if node is None:
                    continue

                size = estimate_node_size(node.label)

                positions[node_id] = NodePosition(
                    node_id=node_id,
                    position=Point(x, y),
                    size=size,
                )

                x += size.width + horizontal_gap

                max_width = max(max_width, x)
                max_height = max(
                    max_height,
                    y + size.height,
                )

        return LayoutResult(
            width=max_width + margin,
            height=max_height + margin,
            nodes=positions,
            metadata={
                "layout": self.name,
                "levels": dict(levels),
            },
        )