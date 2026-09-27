from typing import Dict, Tuple
from app.diagram.models import DiagramIR, DiagramOutputSpec
from app.diagram.layout.base import BaseLayoutStrategy, LayoutResult, NodeGeometry


class GridLayoutStrategy(BaseLayoutStrategy):
    """Arranges nodes into a responsive 2D matrix."""

    def compute_layout(
        self,
        diagram: DiagramIR,
        output_spec: DiagramOutputSpec,
        dimensions: Tuple[int, int],
    ) -> LayoutResult:
        width, height = dimensions
        count = len(diagram.nodes)
        node_boxes: Dict[str, NodeGeometry] = {}

        cols = max(1, min(count, 4))
        rows = (count + cols - 1) // cols if count > 0 else 1

        x_step = width // (cols + 1)
        y_step = height // (rows + 1)
        box_w, box_h = 130, 48

        for idx, node in enumerate(diagram.nodes):
            c_idx = idx % cols
            r_idx = idx // cols
            cx = (c_idx + 1) * x_step
            cy = (r_idx + 1) * y_step

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