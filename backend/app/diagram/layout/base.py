from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Tuple
from app.diagram.models import DiagramIR, DiagramOutputSpec


@dataclass
class NodeGeometry:
    x: int
    y: int
    width: int
    height: int


@dataclass
class LayoutResult:
    node_boxes: Dict[str, NodeGeometry]
    canvas_width: int
    canvas_height: int


class BaseLayoutStrategy(ABC):
    """Abstract strategy for placing nodes and routing edges into geometry."""

    @abstractmethod
    def compute_layout(
        self,
        diagram: DiagramIR,
        output_spec: DiagramOutputSpec,
        dimensions: Tuple[int, int],
    ) -> LayoutResult:
        raise NotImplementedError