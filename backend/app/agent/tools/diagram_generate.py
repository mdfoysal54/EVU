from typing import Any, Dict
from app.diagram.service import generate_diagram_artifact
from app.diagram.validator import ValidationError


def diagram_generate_tool(diagram_ir_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generates an accessible, branded diagram (SVG) from a DiagramIR specification."""
    try:
        svg_content = generate_diagram_artifact(diagram_ir_payload)
        return {
            "status": "success",
            "format": "svg",
            "content": svg_content,
        }
    except ValidationError as err:
        return {
            "status": "error",
            "error_type": "validation_failure",
            "message": str(err),
        }
    except Exception as err:
        return {
            "status": "error",
            "error_type": "render_failure",
            "message": f"Failed to generate diagram: {str(err)}",
        }