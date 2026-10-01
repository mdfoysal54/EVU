from __future__ import annotations
from dataclasses import dataclass, field
from .ir import DiagramIR


class ValidationError(ValueError):
    """Compatibility exception for diagram tool callers."""


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class DiagramValidator:
    def validate(self, diagram: DiagramIR) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        node_ids = diagram.node_ids()
        if not diagram.id: errors.append("Diagram ID is required.")
        if not diagram.diagram_type: errors.append("Diagram type is required.")
        if not diagram.nodes: errors.append("Diagram must contain at least one node.")
        duplicate_ids = self._duplicates([n.id for n in diagram.nodes])
        if duplicate_ids: errors.append("Duplicate node IDs: " + ", ".join(duplicate_ids))
        for edge in diagram.edges:
            if edge.source not in node_ids: errors.append(f"Edge source '{edge.source}' does not exist.")
            if edge.target not in node_ids: errors.append(f"Edge target '{edge.target}' does not exist.")
        group_ids = {g.id for g in diagram.groups}
        for node in diagram.nodes:
            if node.group_id and node.group_id not in group_ids:
                warnings.append(f"Node '{node.id}' references unknown group '{node.group_id}'.")
        if len(diagram.nodes) > 40:
            warnings.append("Diagram contains more than 40 nodes and may become difficult to render.")
        return ValidationResult(valid=not errors, errors=errors, warnings=warnings)

    @staticmethod
    def _duplicates(values: list[str]) -> list[str]:
        seen, duplicates = set(), set()
        for value in values:
            if value in seen: duplicates.add(value)
            seen.add(value)
        return sorted(duplicates)
