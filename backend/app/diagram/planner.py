from __future__ import annotations

from .complexity import DiagramComplexityAnalyzer
from .models import DiagramPlan
from .selector import DiagramTypeSelector
from .semantic.classifier import DiagramClassifier


class DiagramPlanner:
    def __init__(self) -> None:
        self.classifier = DiagramClassifier()
        self.complexity = DiagramComplexityAnalyzer()
        self.selector = DiagramTypeSelector()

    def plan(
        self,
        prompt: str,
        requested_type: str | None = None,
    ) -> DiagramPlan:
        classification = self.classifier.classify(prompt)
        complexity = self.complexity.analyze(prompt)

        diagram_type = self.selector.select(
            classification,
            complexity,
            requested_type,
        )

        direction = self._direction_for(diagram_type)

        reasoning = [
            f"Detected diagram type: {diagram_type}.",
            f"Complexity level: {complexity.level}.",
            f"Estimated nodes: {complexity.estimated_nodes}.",
            f"Estimated edges: {complexity.estimated_edges}.",
        ]

        if classification.matches:
            reasoning.append(
                "Semantic matches: "
                + ", ".join(classification.matches)
                + "."
            )

        return DiagramPlan(
            diagram_type=diagram_type,
            direction=direction,
            confidence=classification.confidence,
            reasoning=reasoning,
            recommended_nodes=complexity.estimated_nodes,
            recommended_edges=complexity.estimated_edges,
        )

    @staticmethod
    def _direction_for(diagram_type: str) -> str:
        return {
            "sequence": "LR",
            "timeline": "LR",
            "quadrant": "TB",
            "layers": "TB",
            "hierarchy": "TB",
            "tree": "TB",
            "architecture": "LR",
            "deployment": "LR",
            "dependency": "LR",
        }.get(diagram_type, "TD")