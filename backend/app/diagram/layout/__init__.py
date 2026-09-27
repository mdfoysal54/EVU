from typing import Tuple
from app.diagram.models import DiagramIR, DiagramOutputSpec
from app.diagram.layout.base import LayoutResult, NodeGeometry, BaseLayoutStrategy
from app.diagram.layout.sequence import SequenceLayoutStrategy
from app.diagram.layout.timeline import TimelineLayoutStrategy
from app.diagram.layout.hierarchy import HierarchyLayoutStrategy
from app.diagram.layout.grid import GridLayoutStrategy


class LayoutEngine:
    """Dispatches semantic diagram types to deterministic geometric layouts."""

    def __init__(self):
        self.sequence_layout = SequenceLayoutStrategy()
        self.timeline_layout = TimelineLayoutStrategy()
        self.hierarchy_layout = HierarchyLayoutStrategy()
        self.grid_layout = GridLayoutStrategy()

    def layout(
        self,
        diagram: DiagramIR,
        output_spec: DiagramOutputSpec,
        dimensions: Tuple[int, int],
    ) -> LayoutResult:
        dtype = (diagram.diagram_type or "").lower()

        if dtype == "sequence":
            return self.sequence_layout.compute_layout(diagram, output_spec, dimensions)
        if dtype in ("timeline", "gantt"):
            return self.timeline_layout.compute_layout(diagram, output_spec, dimensions)
        if dtype in ("tree", "org_chart", "hierarchy"):
            return self.hierarchy_layout.compute_layout(diagram, output_spec, dimensions)

        return self.grid_layout.compute_layout(diagram, output_spec, dimensions)


__all__ = ["LayoutEngine", "LayoutResult", "NodeGeometry", "BaseLayoutStrategy"]