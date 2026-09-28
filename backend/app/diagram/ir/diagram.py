from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .edges import DiagramEdge
from .groups import DiagramGroup
from .nodes import DiagramNode


@dataclass
class DiagramIR:
    id: str
    diagram_type: str
    title: str | None = None

    nodes: list[DiagramNode] = field(default_factory=list)
    edges: list[DiagramEdge] = field(default_factory=list)
    groups: list[DiagramGroup] = field(default_factory=list)

    direction: str = "TD"

    metadata: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: DiagramNode) -> None:
        if any(existing.id == node.id for existing in self.nodes):
            return

        self.nodes.append(node)

        if node.group_id:
            group = self.get_group(node.group_id)
            if group:
                group.add_node(node.id)

    def add_edge(self, edge: DiagramEdge) -> None:
        self.edges.append(edge)

    def add_group(self, group: DiagramGroup) -> None:
        if not self.get_group(group.id):
            self.groups.append(group)

    def get_node(self, node_id: str) -> DiagramNode | None:
        return next(
            (node for node in self.nodes if node.id == node_id),
            None,
        )

    def get_group(self, group_id: str) -> DiagramGroup | None:
        return next(
            (group for group in self.groups if group.id == group_id),
            None,
        )

    def node_ids(self) -> set[str]:
        return {node.id for node in self.nodes}

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "diagram_type": self.diagram_type,
            "title": self.title,
            "direction": self.direction,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "groups": [group.to_dict() for group in self.groups],
            "metadata": self.metadata,
        }

    def to_mermaid(self) -> str:
        lines = [f"flowchart {self.direction}"]

        for node in self.nodes:
            label = self._escape(node.label)
            lines.append(f'    {node.id}["{label}"]')

        for edge in self.edges:
            label = self._escape(edge.label) if edge.label else None

            if edge.style.value == "dashed":
                connector = "-.->"
            elif edge.style.value == "dotted":
                connector = "-..->"
            else:
                connector = "-->"

            if label:
                lines.append(
                    f'    {edge.source} {connector}|"{label}"| {edge.target}'
                )
            else:
                lines.append(
                    f"    {edge.source} {connector} {edge.target}"
                )

        return "\n".join(lines)

    @staticmethod
    def _escape(value: str | None) -> str:
        if not value:
            return ""

        return (
            str(value)
            .replace('"', "'")
            .replace("\n", " ")
        )