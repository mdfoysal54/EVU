from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ComplexityResult:
    score: float
    level: str
    estimated_nodes: int
    estimated_edges: int
    branching: int
    keywords: int


class DiagramComplexityAnalyzer:
    """Estimates how complex a requested diagram is."""

    BRANCH_WORDS = {
        "if",
        "else",
        "branch",
        "decision",
        "condition",
        "parallel",
        "fork",
        "multiple",
        "choice",
    }

    def analyze(self, prompt: str) -> ComplexityResult:
        text = prompt.lower()

        words = text.split()

        keywords = sum(
            1
            for word in words
            if word in {
                "api",
                "database",
                "service",
                "server",
                "client",
                "user",
                "model",
                "agent",
                "workflow",
                "queue",
                "cache",
                "frontend",
                "backend",
            }
        )

        branching = sum(
            1 for word in words if word.strip(".,!?") in self.BRANCH_WORDS
        )

        estimated_nodes = max(
            3,
            min(50, 3 + keywords + len(words) // 8),
        )

        estimated_edges = max(
            2,
            estimated_nodes - 1 + branching,
        )

        score = (
            estimated_nodes * 0.8
            + estimated_edges * 0.4
            + branching * 2
        )

        if score < 12:
            level = "low"
        elif score < 25:
            level = "medium"
        elif score < 45:
            level = "high"
        else:
            level = "very_high"

        return ComplexityResult(
            score=round(score, 2),
            level=level,
            estimated_nodes=estimated_nodes,
            estimated_edges=estimated_edges,
            branching=branching,
            keywords=keywords,
        )


def analyze_complexity(prompt: str) -> ComplexityResult:
    return DiagramComplexityAnalyzer().analyze(prompt)