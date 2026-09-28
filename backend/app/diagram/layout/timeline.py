from __future__ import annotations

from ..ir import DiagramIR
from .base import (
    LayoutEngine,
    LayoutResult,
    NodePosition,
    Point,
    estimate_node_size,
)


class TimelineLayout(LayoutEngine):
    name = "timeline"

    def layout(
        self,
        diagram: DiagramIR,
        *,
        gap: float = 80,
        margin: float = 50,
        **kwargs,
    ) -> LayoutResult:

        positions: dict[str, NodePosition] = {}

        x = margin
        y = margin

        for index, node in enumerate(diagram.nodes):
            size = estimate_node_size(node.label)

            positions[node.id] = NodePosition(
                node_id=node.id,
                position=Point(
                    x,
                    y + (30 if index % 2 else 0),
                ),
                size=size,
            )

            x += size.width + gap

        return LayoutResult(
            width=x + margin,
            height=220,
            nodes=positions,
            metadata={
                "layout": self.name,
                "timeline_axis": y + 90,
            },
        )