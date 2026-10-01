from __future__ import annotations
from typing import Any
from .models import DiagramRequestModel, DiagramResult, DiagramOutputSpec, DiagramFormat
from .planner import DiagramPlanner
from .types import BUILDERS
from .validator import DiagramValidator


class DiagramService:
    def __init__(self, planner=None, validator=None):
        self.planner = planner or DiagramPlanner()
        self.validator = validator or DiagramValidator()

    def generate(self, request: DiagramRequestModel) -> DiagramResult:
        plan = self.planner.plan(request.prompt, request.diagram_type)
        builder = BUILDERS.get(plan.diagram_type)
        if builder is None:
            raise ValueError(f"No builder registered for diagram type '{plan.diagram_type}'.")
        diagram = builder(request.prompt, request.title)
        diagram.direction = plan.direction
        diagram.metadata.update({"planner_confidence": plan.confidence, "reasoning": plan.reasoning})
        validation = self.validator.validate(diagram)
        if not validation.valid:
            raise ValueError("Generated diagram failed validation: " + "; ".join(validation.errors))
        return DiagramResult(diagram=diagram, plan=plan, warnings=validation.warnings)


def _payload_to_request(payload: dict[str, Any]) -> DiagramRequestModel:
    return DiagramRequestModel(
        prompt=str(payload.get("prompt") or payload.get("description") or "Generate a diagram."),
        diagram_type=payload.get("diagram_type") or payload.get("type"),
        title=payload.get("title"),
        options=payload.get("options") or {},
    )


def generate_diagram_artifact(payload: dict[str, Any], output_spec: DiagramOutputSpec | None = None):
    """Compatibility API for the agent diagram tools.

    The canonical engine is DiagramService. This wrapper accepts either a
    generation request or a basic DiagramIR-like payload and returns SVG/HTML.
    """
    spec = output_spec or DiagramOutputSpec()
    result = diagram_service.generate(_payload_to_request(payload))
    if spec.format == DiagramFormat.SVG:
        from .renderers.svg import SVGRenderer
        return SVGRenderer().render(result.diagram)
    if spec.format == DiagramFormat.HTML:
        from html import escape
        svg = generate_diagram_artifact(payload, DiagramOutputSpec(DiagramFormat.SVG, spec.size))
        return f"<!doctype html><html><body>{svg}<pre>{escape(result.mermaid)}</pre></body></html>"
    if spec.format == DiagramFormat.PNG:
        from .renderers.png import PNGRenderer
        return PNGRenderer().render(result.diagram)
    raise ValueError(f"Unsupported diagram format: {spec.format}")


diagram_service = DiagramService()
