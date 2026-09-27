from typing import Dict, Tuple
from app.diagram.models import DiagramIR, DiagramOutputSpec
from app.diagram.layout.base import BaseLayoutStrategy, LayoutResult, NodeGeometry


class TimelineLayoutStrategy(BaseLayoutStrategy):
    """Arranges milestones along a horizontal baseline."""

    def compute_layout(
        self,
        diagram: DiagramIR,
        output_spec: DiagramOutputSpec,
        dimensions: Tuple[int, int],
    ) -> LayoutResult:
        width, height = dimensions
        count = len(diagram.nodes)
        node_boxes: Dict[str, NodeGeometry] = {}

        box_w, box_h = 130, 48
        spacing = width // (count + 1) if count > 0 else width // 2
        center_y = height // 2

        for idx, node in enumerate(diagram.nodes):
            cx = (idx + 1) * spacing
            # Alternate nodes above and below the spine
            offset = -70 if idx % 2 == 0 else 70
            node_boxes[node.id] = NodeGeometry(
                x=cx - (box_w // 2),
                y=(center_y + offset) - (box_h // 2),
                width=box_w,
                height=box_h,
            )

        return LayoutResult(
            node_boxes=node_boxes,
            canvas_width=width,
            canvas_height=height,
        )