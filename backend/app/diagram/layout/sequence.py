from typing import Dict, Tuple
from app.diagram.models import DiagramIR, DiagramOutputSpec
from app.diagram.layout.base import BaseLayoutStrategy, LayoutResult, NodeGeometry


class SequenceLayoutStrategy(BaseLayoutStrategy):
    """Positions actors horizontally along the top with vertical lifelines."""

    def compute_layout(
        self,
        diagram: DiagramIR,
        output_spec: DiagramOutputSpec,
        dimensions: Tuple[int, int],
    ) -> LayoutResult:
        width, height = dimensions
        count = len(diagram.nodes)
        node_boxes: Dict[str, NodeGeometry] = {}

        box_w, box_h = 120, 44
        col_gap = width // (count + 1) if count > 0 else width // 2

        for idx, node in enumerate(diagram.nodes):
            cx = (idx + 1) * col_gap
            cy = 60
            node_boxes[node.id] = NodeGeometry(
                x=cx - (box_w // 2),
                y=cy - (box_h // 2),
                width=box_w,
                height=box_h,
            )

        return LayoutResult(
            node_boxes=node_boxes,
            canvas_width=width,
            canvas_height=height,
        )