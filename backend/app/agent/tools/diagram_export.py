from typing import Any, Dict
from app.diagram.models import DiagramFormat, DiagramOutputSpec, DiagramSize
from app.diagram.service import generate_diagram_artifact


def diagram_export_tool(
    diagram_ir_payload: Dict[str, Any],
    format: str = "svg",
    size: str = "doc-wide",
) -> Dict[str, Any]:
    """Exports a diagram into SVG, HTML, or PNG matching target dimensions."""
    try:
        spec = DiagramOutputSpec(
            format=DiagramFormat(format.lower()),
            size=DiagramSize(size.lower()),
        )
        content = generate_diagram_artifact(diagram_ir_payload, output_spec=spec)
        return {
            "status": "success",
            "format": format,
            "data": content,
        }
    except Exception as err:
        return {
            "status": "error",
            "message": f"Export failed: {str(err)}",
        }