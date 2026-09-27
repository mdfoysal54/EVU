from typing import Any, Dict
from app.diagram.parsers.mermaid import SafeMermaidParser
from app.diagram.validator import DiagramValidator


def diagram_import_tool(source_syntax: str, format_type: str = "mermaid") -> Dict[str, Any]:
    """Parses untrusted diagram syntax (Mermaid, Draw.io) into sanitized EVU DiagramIR."""
    try:
        if format_type.lower() == "mermaid":
            ir = SafeMermaidParser.parse(source_syntax)
        else:
            return {
                "status": "error",
                "message": f"Format '{format_type}' is not yet supported for import.",
            }

        validator = DiagramValidator()
        validator.validate(ir)

        return {
            "status": "success",
            "diagram_ir": {
                "title": ir.title,
                "diagram_type": ir.diagram_type,
                "nodes": [{"id": n.id, "label": n.label, "kind": n.kind} for n in ir.nodes],
                "edges": [{"source": e.source, "target": e.target, "label": e.label} for e in ir.edges],
            },
        }
    except Exception as err:
        return {
            "status": "error",
            "message": f"Failed to parse diagram: {str(err)}",
        }