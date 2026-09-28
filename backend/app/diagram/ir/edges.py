from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EdgeType(str, Enum):
    FLOW = "flow"
    DEPENDENCY = "dependency"
    ASSOCIATION = "association"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    MESSAGE = "message"
    DATA = "data"
    CONTROL = "control"
    TRANSITION = "transition"


class EdgeStyle(str, Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"


@dataclass
class DiagramEdge:
    source: str
    target: str
    label: str | None = None
    edge_type: EdgeType = EdgeType.FLOW
    style: EdgeStyle = EdgeStyle.SOLID
    directed: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "label": self.label,
            "edge_type": self.edge_type.value,
            "style": self.style.value,
            "directed": self.directed,
            "metadata": self.metadata,
        }


def make_edge(
    source: str,
    target: str,
    label: str | None = None,
    edge_type: EdgeType = EdgeType.FLOW,
    *,
    style: EdgeStyle = EdgeStyle.SOLID,
    directed: bool = True,
    metadata: dict[str, Any] | None = None,
) -> DiagramEdge:
    return DiagramEdge(
        source=source,
        target=target,
        label=label,
        edge_type=edge_type,
        style=style,
        directed=directed,
        metadata=metadata or {},
    )