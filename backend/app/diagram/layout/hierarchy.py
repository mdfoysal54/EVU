from __future__ import annotations

from collections import defaultdict

from ..ir import DiagramIR
from .base import (
    LayoutEngine,
    LayoutResult,
    NodePosition,
    Point,
    estimate_node_size,
)


class HierarchyLayout(LayoutEngine):
    name = "hierarchy"

    def layout(
        self,
        diagram: DiagramIR,
        *,
        level_gap: float = 110,
        node_gap: float = 50,
        margin: float = 50,
        **kwargs,
    ) -> LayoutResult:

        children: dict[str, list[str]] = defaultdict(list)
        incoming: dict[str, int] = {
            node.id: 0
            for node in diagram.nodes
        }

        for edge in diagram.edges:
            if edge.source in incoming and edge.target in incoming:
                children[edge.source].append(edge.target)
                incoming[edge.target] += 1

        roots = [
            node_id
            for node_id, count in incoming.items()
            if count == 0
        ]

        if not roots and diagram.nodes:
            roots = [diagram.nodes[0].id]

        levels: dict[str, int] = {}

        def visit(node_id: str, level: int) -> None:
            current = levels.get(node_id)

            if current is not None and current >= level:
                return

            levels[node_id] = level

            for child in children[node_id]:
                visit(child, level + 1)

        for root in roots:
            visit(root, 0)

        for node in diagram.nodes:
            levels.setdefault(node.id, 0)

        grouped: dict[int, list[str]] = defaultdict(list)

        for node_id, level in levels.items():
            grouped[level].append(node_id)

        positions: dict[str, NodePosition] = {}

        canvas_width = 0
        canvas_height = 0

        for level in sorted(grouped):
            node_ids = grouped[level]

            widths = []

            for node_id in node_ids:
                node = diagram.get_node(node_id)
                if node:
                    widths.append(
                        estimate_node_size(node.label)
                    )

            total_width = sum(
                size.width
                for size in widths
            )

            if len(widths) > 1:
                total_width += node_gap * (len(widths) - 1)

            start_x = max(
                margin,
                (canvas_width - total_width) / 2,
            )

            y = margin + level * level_gap

            x = start_x

            for node_id in node_ids:
                node = diagram.get_node(node_id)

                if not node:
                    continue

                size = estimate_node_size(node.label)

                positions[node_id] = NodePosition(
                    node_id=node_id,
                    position=Point(x, y),
                    size=size,
                )

                x += size.width + node_gap

                canvas_width = max(
                    canvas_width,
                    x + margin,
                )

                canvas_height = max(
                    canvas_height,
                    y + size.height + margin,
                )

        return LayoutResult(
            width=max(canvas_width, 300),
            height=max(canvas_height, 200),
            nodes=positions,
            metadata={
                "layout": self.name,
                "levels": levels,
            },
        )