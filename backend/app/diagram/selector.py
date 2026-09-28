from __future__ import annotations

from .complexity import ComplexityResult
from .semantic.classifier import Classification


SUPPORTED_TYPES = {
    "architecture",
    "flowchart",
    "sequence",
    "state",
    "er",
    "timeline",
    "swimlane",
    "quadrant",
    "tree",
    "hierarchy",
    "layers",
    "data_flow",
    "deployment",
    "dependency",
}


class DiagramTypeSelector:
    def select(
        self,
        classification: Classification,
        complexity: ComplexityResult,
        requested_type: str | None = None,
    ) -> str:
        if requested_type:
            normalized = requested_type.strip().lower()

            if normalized not in SUPPORTED_TYPES:
                raise ValueError(
                    f"Unsupported diagram type: {requested_type}"
                )

            return normalized

        selected = classification.diagram_type

        if selected not in SUPPORTED_TYPES:
            return "flowchart"

        return selected