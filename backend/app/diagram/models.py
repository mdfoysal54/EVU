from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .ir import DiagramIR


@dataclass
class DiagramRequestModel:
    prompt: str
    diagram_type: str | None = None
    title: str | None = None
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagramPlan:
    diagram_type: str
    direction: str
    confidence: float
    reasoning: list[str] = field(default_factory=list)
    recommended_nodes: int | None = None
    recommended_edges: int | None = None


@dataclass
class DiagramResult:
    diagram: DiagramIR
    plan: DiagramPlan
    warnings: list[str] = field(default_factory=list)

    @property
    def mermaid(self) -> str:
        return self.diagram.to_mermaid()