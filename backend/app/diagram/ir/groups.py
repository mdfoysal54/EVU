from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiagramGroup:
    id: str
    label: str
    group_type: str = "group"
    parent_id: str | None = None
    node_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node_id: str) -> None:
        if node_id not in self.node_ids:
            self.node_ids.append(node_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "group_type": self.group_type,
            "parent_id": self.parent_id,
            "node_ids": self.node_ids,
            "metadata": self.metadata,
        }