from typing import Any, Dict
from app.diagram.models import (
    DiagramIR,
    DiagramNode,
    DiagramEdge,
    DiagramFormat,
    DiagramSize,
)
from app.diagram.validator import DiagramValidator
from app.diagram.design.tokens import DEFAULT_THEME, DiagramTheme
from app.diagram.renderers import SVGRenderer, HTMLRenderer, PNGRenderer
from app.diagram.schemas import DiagramOutputSpec


def generate_diagram_artifact(
    diagram_ir_payload: Dict[str, Any], 
    theme: DiagramTheme = DEFAULT_THEME,
    output_spec: DiagramOutputSpec | None = None
) -> str:
    if output_spec is None:
        output_spec = DiagramOutputSpec(
            format=DiagramFormat.SVG,
            size=DiagramSize.DOC_WIDE
        )

    # 1. Parse into DiagramIR
    nodes = [
        DiagramNode(
            id=n["id"],
            label=n["label"],
            kind=n.get("kind", "component"),
            group=n.get("group"),
            metadata=n.get("metadata", {})
        )
        for n in diagram_ir_payload.get("nodes", [])
    ]
    edges = [
        DiagramEdge(
            source=e["source"],
            target=e["target"],
            label=e.get("label"),
            kind=e.get("kind", "directed"),
            metadata=e.get("metadata", {})
        )
        for e in diagram_ir_payload.get("edges", [])
    ]

    ir = DiagramIR(
        title=diagram_ir_payload.get("title", "Untitled Diagram"),
        diagram_type=diagram_ir_payload.get("diagram_type", "architecture"),
        nodes=nodes,
        edges=edges,
        groups=diagram_ir_payload.get("groups", []),
        metadata=diagram_ir_payload.get("metadata", {})
    )

    # 2. Validation
    validator = DiagramValidator()
    validator.validate(ir)

    # 3. Dynamic Renderer Selection
    if output_spec.format == DiagramFormat.HTML:
        renderer = HTMLRenderer()
    elif output_spec.format == DiagramFormat.PNG:
        renderer = PNGRenderer()
    else:
        renderer = SVGRenderer()

    return renderer.render(ir, theme, output_spec)