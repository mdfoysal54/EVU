from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeShape(str, Enum):
    RECTANGLE = "rectangle"
    ROUNDED = "rounded"
    CIRCLE = "circle"
    DIAMOND = "diamond"
    CYLINDER = "cylinder"
    HEXAGON = "hexagon"
    PARALLELOGRAM = "parallelogram"
    DOCUMENT = "document"
    ACTOR = "actor"
    CLOUD = "cloud"


@dataclass
class NodeStyle:
    shape: NodeShape = NodeShape.ROUNDED
    classes: list[str] = field(default_factory=list)
    color: str | None = None
    background: str | None = None
    border: str | None = None
    icon: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "shape": self.shape.value,
            "classes": self.classes,
            "color": self.color,
            "background": self.background,
            "border": self.border,
            "icon": self.icon,
        }


@dataclass
class DiagramNode:
    id: str
    label: str
    node_type: str = "component"
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    style: NodeStyle = field(default_factory=NodeStyle)
    group_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "node_type": self.node_type,
            "description": self.description,
            "metadata": self.metadata,
            "style": self.style.to_dict(),
            "group_id": self.group_id,
        }


def make_node(
    node_id: str,
    label: str,
    node_type: str = "component",
    *,
    description: str | None = None,
    group_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    shape: NodeShape = NodeShape.ROUNDED,
) -> DiagramNode:
    return DiagramNode(
        id=node_id,
        label=label,
        node_type=node_type,
        description=description,
        group_id=group_id,
        metadata=metadata or {},
        style=NodeStyle(shape=shape),
    )