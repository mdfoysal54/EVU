from __future__ import annotations

from .base import (
    LayoutEngine,
    LayoutResult,
    NodePosition,
    Point,
    Size,
    estimate_node_size,
)
from .graph import GraphLayout
from .grid import GridLayout
from .hierarchy import HierarchyLayout
from .sequence import SequenceLayout
from .timeline import TimelineLayout


LAYOUTS = {
    "graph": GraphLayout,
    "hierarchy": HierarchyLayout,
    "sequence": SequenceLayout,
    "timeline": TimelineLayout,
    "grid": GridLayout,
}


def get_layout(name: str) -> LayoutEngine:
    layout_class = LAYOUTS.get(name)

    if layout_class is None:
        raise ValueError(
            f"Unknown diagram layout: {name}"
        )

    return layout_class()


def select_layout(diagram_type: str) -> LayoutEngine:
    mapping = {
        "sequence": "sequence",
        "timeline": "timeline",
        "hierarchy": "hierarchy",
        "tree": "hierarchy",
        "uml": "graph",
        "database": "graph",
        "architecture": "graph",
        "deployment": "graph",
        "dependency": "graph",
        "layers": "hierarchy",
        "quadrant": "grid",
        "flowchart": "graph",
        "state": "graph",
        "er": "graph",
        "data_flow": "graph",
        "swimlane": "graph",
    }

    layout_name = mapping.get(
        diagram_type,
        "graph",
    )

    return get_layout(layout_name)


__all__ = [
    "LayoutEngine",
    "LayoutResult",
    "NodePosition",
    "Point",
    "Size",
    "GraphLayout",
    "GridLayout",
    "HierarchyLayout",
    "SequenceLayout",
    "TimelineLayout",
    "LAYOUTS",
    "get_layout",
    "select_layout",
    "estimate_node_size",
]