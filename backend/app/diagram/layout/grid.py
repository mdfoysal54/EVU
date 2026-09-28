from __future__ import annotations

import math

from ..ir import DiagramIR
from .base import (
    LayoutEngine,
    LayoutResult,
    NodePosition,
    Point,
    estimate_node_size,
)


class GridLayout(LayoutEngine):
    name = "grid"

    def layout(
        self,
        diagram: DiagramIR,
        *,
        columns: int | None = None,
        column_gap: float = 60,
        row_gap: float = 60,
        margin: float = 40,
        **kwargs,
    ) -> LayoutResult:

        count = len(diagram.nodes)

        if count == 0:
            return LayoutResult(0, 0)

        if columns is None:
            columns = max(
                1,
                math.ceil(math.sqrt(count)),
            )

        positions: dict[str, NodePosition] = {}

        row_heights: dict[int, float] = {}

        for index, node in enumerate(diagram.nodes):
            row = index // columns
            column = index % columns

            size = estimate_node_size(node.label)

            row_heights[row] = max(
                row_heights.get(row, 0),
                size.height,
            )

            x = margin + column * (
                180 + column_gap
            )

            y = margin + row * (
                56 + row_gap
            )

            positions[node.id] = NodePosition(
                node_id=node.id,
                position=Point(x, y),
                size=size,
            )

        rows = math.ceil(count / columns)

        width = (
            margin * 2
            + columns * 180
            + max(0, columns - 1) * column_gap
        )

        height = (
            margin * 2
            + rows * 56
            + max(0, rows - 1) * row_gap
        )

        return LayoutResult(
            width=width,
            height=height,
            nodes=positions,
            metadata={
                "layout": self.name,
                "columns": columns,
                "rows": rows,
            },
        )