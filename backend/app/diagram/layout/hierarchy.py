from collections import defaultdict
from typing import Dict, List, Tuple
from app.diagram.models import DiagramIR, DiagramOutputSpec
from app.diagram.layout.base import BaseLayoutStrategy, LayoutResult, NodeGeometry


class HierarchyLayoutStrategy(BaseLayoutStrategy):
    """Calculates levels from graph edges and distributes nodes by layer."""

    def compute_layout(
        self,
        diagram: DiagramIR,
        output_spec: DiagramOutputSpec,
        dimensions: Tuple[int, int],
    ) -> LayoutResult:
        width, height = dimensions
        box_w, box_h = 130, 46
        node_boxes: Dict[str, NodeGeometry] = {}

        # 1. Determine tree depths
        incoming: Dict[str, int] = {node.id: 0 for node in diagram.nodes}
        children: Dict[str, List[str]] = defaultdict(list)
        for edge in diagram.edges:
            incoming[edge.target] = incoming.get(edge.target, 0) + 1
            children[edge.source].append(edge.target)

        roots = [nid for nid, deg in incoming.items() if deg == 0] or [diagram.nodes[0].id]
        levels: Dict[int, List[str]] = defaultdict(list)
        visited = set()

        def dfs(node_id: str, depth: int):
            if node_id in visited:
                return
            visited.add(node_id)
            levels[depth].append(node_id)
            for ch in children[node_id]:
                dfs(ch, depth + 1)

        for root in roots:
            dfs(root, 0)

        # Include orphan nodes on level 0
        for n in diagram.nodes:
            if n.id not in visited:
                levels[0].append(n.id)

        total_depth = len(levels)
        y_step = height // (total_depth + 1 or 1)

        for depth, nids in levels.items():
            cy = (depth + 1) * y_step
            x_step = width // (len(nids) + 1 or 1)
            for idx, nid in enumerate(nids):
                cx = (idx + 1) * x_step
                node_boxes[nid] = NodeGeometry(
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