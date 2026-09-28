from __future__ import annotations

from dataclasses import dataclass, field

from .registry import SemanticPatternRegistry


@dataclass
class Classification:
    diagram_type: str
    confidence: float
    matches: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)


class DiagramClassifier:
    def __init__(self, registry: SemanticPatternRegistry | None = None) -> None:
        self.registry = registry or SemanticPatternRegistry()

    def classify(self, prompt: str) -> Classification:
        text = prompt.lower()

        scores: dict[str, float] = {}

        for pattern in self.registry.all():
            score = 0.0

            for keyword in pattern.keywords:
                if keyword in text:
                    score += 1.0

            if score:
                score += pattern.priority * 0.1
                scores[pattern.diagram_type] = (
                    scores.get(pattern.diagram_type, 0.0) + score
                )

        if not scores:
            return Classification(
                diagram_type="flowchart",
                confidence=0.25,
                matches=[],
                scores={},
            )

        ordered = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        best_type, best_score = ordered[0]

        total = sum(scores.values()) or 1.0
        confidence = min(0.99, best_score / total)

        matches = [
            pattern.name
            for pattern in self.registry.all()
            if pattern.diagram_type == best_type
        ]

        return Classification(
            diagram_type=best_type,
            confidence=round(confidence, 3),
            matches=matches,
            scores=scores,
        )