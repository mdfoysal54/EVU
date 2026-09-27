from typing import Any, Dict
from app.diagram.service import generate_diagram_artifact
from app.diagram.validator import ValidationError


def diagram_tool(diagram_ir_payload: Dict[str, Any]) -> Dict[str, Any]:
    """EVU Agent Tool: Consumes a DiagramIR dictionary and returns validated SVG."""
    try:
        svg_content = generate_diagram_artifact(diagram_ir_payload)
        return {
            "status": "success",
            "format": "svg",
            "content": svg_content
        }
    except ValidationError as err:
        return {
            "status": "error",
            "error_type": "validation_failure",
            "message": str(err)
        }
    except Exception as err:
        return {
            "status": "error",
            "error_type": "render_failure",
            "message": f"Failed to render diagram: {str(err)}"
        }