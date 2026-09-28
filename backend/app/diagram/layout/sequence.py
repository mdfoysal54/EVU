from __future__ import annotations

from ..ir import DiagramIR
from .base import (
    LayoutEngine,
    LayoutResult,
    NodePosition,
    Point,
    estimate_node_size,
)


class SequenceLayout(LayoutEngine):
    name = "sequence"

    def layout(
        self,
        diagram: DiagramIR,
        *,
        participant_gap: float = 180,
        margin: float = 50,
        **kwargs,
    ) -> LayoutResult:

        positions: dict[str, NodePosition] = {}

        x = margin
        max_height = 250

        for node in diagram.nodes:
            size = estimate_node_size(
                node.label,
                min_width=140,
            )

            positions[node.id] = NodePosition(
                node_id=node.id,
                position=Point(
                    x,
                    margin,
                ),
                size=size,
            )

            x += size.width + participant_gap

        return LayoutResult(
            width=max(x + margin, 500),
            height=max_height,
            nodes=positions,
            metadata={
                "layout": self.name,
                "lifelines": True,
            },
        )