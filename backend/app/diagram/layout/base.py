from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..ir import DiagramIR


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Size:
    width: float
    height: float


@dataclass
class NodePosition:
    node_id: str
    position: Point
    size: Size

    @property
    def x(self) -> float:
        return self.position.x

    @property
    def y(self) -> float:
        return self.position.y

    @property
    def width(self) -> float:
        return self.size.width

    @property
    def height(self) -> float:
        return self.size.height


@dataclass
class LayoutResult:
    width: float
    height: float
    nodes: dict[str, NodePosition] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, node_id: str) -> NodePosition | None:
        return self.nodes.get(node_id)


class LayoutEngine:
    """
    Base interface for all diagram layouts.
    """

    name = "base"

    def layout(
        self,
        diagram: DiagramIR,
        **kwargs: Any,
    ) -> LayoutResult:
        raise NotImplementedError


def estimate_node_size(
    label: str,
    *,
    min_width: float = 120,
    height: float = 56,
) -> Size:
    """
    Simple text-based size estimation.

    Renderers can later replace this with font-aware measurement.
    """

    width = max(
        min_width,
        min(360, len(label) * 8 + 36),
    )

    return Size(
        width=float(width),
        height=float(height),
    )